import uuid

import reversion
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django_fsm import FSMField, transition
import templated_email


# ISO/IEC 5218
SEX_CHOICES = (
    ('0', 'not known'),
    ('1', 'male'),
    ('2', 'female'),
    ('9', 'not applicable'),
)

# ISO/IEC 24760-1:2011
STATE_CHOICES = (
    ('established', 'established'),
    ('active', 'active'),
    ('archived', 'archived'),
    ('suspended', 'suspended'),
    ('merged', 'merged'), # Not in standard, but used for operational purposes
)

def get_uuid():
    return uuid.uuid4()


class User(AbstractBaseUser):
    uuid = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    identity = models.ForeignKey('identity.Identity', null=True, blank=True)


class IdentityType(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    label = models.TextField()


class PersonManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_id='person')


class OrganizationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_id='organization')


class Identity(DirtyFieldsMixin, models.Model):
    """An identity is the information used to represent an entity in an ICT system.

    The purpose of the ICT system determines which of the attributes describing an entity are used for an identity.
    Within an ICT system an identity shall be the set of those attributes related to an entity which are relevant to
    the particular domain of application served by the ICT system. Depending on the specific requirements of this
    domain, this set of attributes related to the entity (the identity) may, but does not have to be, uniquely
    distinguishable from other identities in the ICT system. (taken from ISO/IEC 24760-1:2011)
    """
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    type = models.ForeignKey(IdentityType)
    label = models.CharField(max_length=1024, blank=True)
    qualified_label = models.CharField(max_length=1024, blank=True)
    sort_label = models.CharField(max_length=1024, blank=True)
    state = FSMField(choices=STATE_CHOICES, default='established')
    merged_into = models.ForeignKey('self', null=True, blank=True, related_name='merged_from')

    # Generic
    primary_email = models.EmailField(blank=True)
    primary_username = models.CharField(blank=True, max_length=32)
    begin_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    extant = models.BooleanField(default=True)

    # People
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='0')
    primary_name = models.OneToOneField('name.Name', related_name='primary_name_of', null=True, blank=True, default=None)

    # Application
    pass

    # Organization
    pass

    # Organization Role
    organization = models.ForeignKey('self', related_name='role_identity', null=True, blank=True)
    role_type = models.ForeignKey('relationship.RoleType', null=True, blank=True)
    role_label = models.CharField(max_length=1024, blank=True)

    # matriculation_date
    # photo

    claim_code = models.UUIDField(null=True, blank=True)

    objects = models.Manager()
    people = PersonManager()
    organizations = OrganizationManager()

    class Meta:
        verbose_name = 'identity'
        verbose_name_plural = 'identities'

    def natural_key(self):
        return self.uuid

    def __str__(self):
        try:
            return self.primary_name.plain
        except Exception:
            return self.primary_email or str(self.id)

    @transition(field=state, source='established', target='established',
                conditions=[lambda self: self.emails.exists()])
    def ready_for_activation(self, email=None):
        if not email:
            email = self.emails.order_by('order').first().value
        self.claim_code = get_uuid()
        templated_email.send_templated_mail(template_name='claim-identity',
                                            from_email=settings.DEFAULT_FROM_EMAIL,
                                            to_email=email,
                                            context={'identity': self,
                                                     'claim_url': settings.CLAIM_URL.format(self.claim_code)})

    @transition(field=state, source='established', target='active')
    def activate(self):
        pass

    @transition(field=state, source='active', target='archived')
    def archive(self):
        pass

    @transition(field=state, source='archived', target='established')
    def restore(self):
        pass

    @transition(field=state, source=['established', 'active'], target='merged')
    def merge_into(self, other):
        self.merged_into = other

    @transition(field=state, source='active', target='suspended')
    def suspend(self, other):
        pass

    @transition(field=state, source='suspended', target='active')
    def reactivate(self, other):
        pass

    def save(self, *args, **kwargs):
        if self.type_id == 'person':
            if self.primary_name:
                self.label = self.primary_name.plain
                self.qualified_label = self.primary_name.plain_full
                self.sort_label = self.primary_name.sort
            else:
                self.label = self.qualified_label = self.sort_label = ''
        if self.type_id == 'organization-role':
            self.label = self.role_label or self.role_type.label
            self.qualified_label = ', '.join([self.label, self.organization.label])
            self.sort_label = ', '.join([self.organization.label, self.label])
        elif self.type_id == 'organization':
            pass
        return super().save(*args, **kwargs)

reversion.register(Identity)
