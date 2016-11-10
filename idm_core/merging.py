import collections.abc
from django.conf import settings
from django.db import transaction, connection

from idm_core import broker
from idm_core.identifier.models import Identifier
from idm_core.nationality.models import Nationality
from idm_core.org_relationship.models import Affiliation, Role
from .attestation.models import SourceDocument
from .name.models import Name

_fields_to_copy = {'primary_email', 'primary_username', 'date_of_birth',
                   'date_of_death'}

def merge(merge_these, into_this, trigger=None, reason=None):
    with transaction.atomic():
        if not isinstance(merge_these, collections.abc.Iterable):
            merge_these = (merge_these,)

        for source_document in SourceDocument.objects.filter(person__in=merge_these):
            source_document.person = into_this
            source_document.save()

        names = set(name.marked_up for name in into_this.names.all())
        for name in Name.objects.filter(person__in=merge_these):
            if name.marked_up in names:
                name.attestations.all().delete()
                name.delete()
            else:
                name.person = into_this
                name.save()

        nationalities = into_this.nationalities.all()
        for nationality in Nationality.objects.filter(person__in=merge_these):
            if nationality.country in nationalities:

                nationality.attestations.all().delete()
                nationality.delete()
            else:
                nationality.person = into_this
                nationality.save()

        for affiliation in Affiliation.objects.filter(person__in=merge_these):
            affiliation.person = into_this
            affiliation.save()

        for role in Role.objects.filter(person__in=merge_these):
            role.person = into_this
            role.save()

        for identifier in Identifier.objects.filter(person__in=merge_these):
            identifier.person = into_this
            identifier.save()

        for person in merge_these:
            for field_name in _fields_to_copy:
                if getattr(person, field_name) and not getattr(into_this, field_name):
                    setattr(into_this, field_name, getattr(person, field_name))
            if person.sex != '0' and into_this.sex == '0':
                into_this.sex = person.sex
            person.merge_into(into_this)
            person.save()

        into_this.save()

    connection.on_commit(lambda : publish_merge_to_amqp(merge_these, into_this))


def publish_merge_to_amqp(merge_these, into_this):
    with broker.connection.acquire(block=True) as conn:
        producer = conn.Producer(serializer='json')
        producer.publish({'mergedPeople': [person.id for person in merge_these],
                          'targetPerson': into_this.id},
                         exchange=settings.BROKER_PREFIX + 'person',
                         routing_key='{}.{}.{}'.format(type(into_this).__name__,
                                                       'merged',
                                                       into_this.pk))
