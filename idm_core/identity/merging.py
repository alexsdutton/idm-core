import collections.abc
from django.conf import settings
from django.db import transaction, connection

from idm_core.identifier.models import Identifier
from idm_core.nationality.models import Nationality
from idm_core.relationship.models import Affiliation, Role
from idm_notification import broker
from idm_core.attestation.models import SourceDocument
from idm_core.name.models import Name

_fields_to_copy = {'primary_email', 'primary_username', 'begin_date', 'end_date', 'extant'}


class MergeTypeDisparity(Exception):
    pass


def merge(merge_these, into_this, trigger=None, reason=None):
    with transaction.atomic():
        if not isinstance(merge_these, collections.abc.Iterable):
            merge_these = (merge_these,)

        for identity in merge_these:
            if identity.type_id != into_this.type_id:
                raise MergeTypeDisparity("Type of {} ({}) does not match that of {} ({})".format(
                    identity.id, identity.type_id, into_this.id, into_this.type_id
                ))

        for source_document in SourceDocument.objects.filter(identity__in=merge_these):
            source_document.person = into_this
            source_document.save()

        names = set(name.marked_up for name in into_this.names.all())
        for name in Name.objects.filter(identity__in=merge_these):
            if name.marked_up in names:
                name.attestations.all().delete()
                name.delete()
            else:
                name.identity = into_this
                name.save()

        nationalities = into_this.nationalities.all()
        for nationality in Nationality.objects.filter(identity__in=merge_these):
            if nationality.country in nationalities:

                nationality.attestations.all().delete()
                nationality.delete()
            else:
                nationality.identity = into_this
                nationality.save()

        for affiliation in Affiliation.objects.filter(identity__in=merge_these):
            affiliation.identity = into_this
            affiliation.save()

        for role in Role.objects.filter(identity__in=merge_these):
            role.identity = into_this
            role.save()

        for identifier in Identifier.objects.filter(identity__in=merge_these):
            identifier.identity = into_this
            identifier.save()

        for identity in merge_these:
            for field_name in _fields_to_copy:
                if getattr(identity, field_name) and not getattr(into_this, field_name):
                    setattr(into_this, field_name, getattr(identity, field_name))
            if identity.sex != '0' and into_this.sex == '0':
                into_this.sex = identity.sex
            identity.merge_into(into_this)
            identity.save()

        into_this.save()

    connection.on_commit(lambda : publish_merge_to_amqp(merge_these, into_this))


def publish_merge_to_amqp(merge_these, into_this):
    with broker.connection.acquire(block=True) as conn:
        producer = conn.Producer(serializer='json')
        producer.publish({'mergedIdentities': [identity.id for identity in merge_these],
                          'targetIdentity': into_this.id},
                         exchange=settings.BROKER_PREFIX + 'identity',
                         routing_key='{}.{}.{}'.format(type(into_this).__name__,
                                                       'merged',
                                                       into_this.pk))
