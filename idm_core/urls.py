from django.conf.urls import include, url
from django.contrib import admin
from rest_framework_nested import routers

import idm_core.attestation.views
import idm_core.contact.views
import idm_core.identifier.views
import idm_core.name.views
import idm_core.nationality.views
import idm_core.relationship.views
import idm_core.organization.views
import idm_core.identity.views

router = routers.DefaultRouter()
router.register('identity', idm_core.identity.views.IdentityViewSet, 'identity')
router.register('person', idm_core.identity.views.PersonViewSet)
router.register('country', idm_core.nationality.views.CountryViewSet)
router.register('affiliation-type', idm_core.relationship.views.AffiliationTypeViewSet)
router.register('role-type', idm_core.relationship.views.RoleTypeViewSet)
router.register('identifier-type', idm_core.identifier.views.IdentifierTypeViewSet)
router.register('organization', idm_core.organization.views.OrganizationViewSet)

person_router = routers.NestedSimpleRouter(router, r'person', lookup='person')
person_router.register('nationality', idm_core.nationality.views.NationalityViewSet, base_name='identity-nationality')
person_router.register('affiliation', idm_core.relationship.views.AffiliationViewSet, base_name='identity-affiliation')
person_router.register('role', idm_core.relationship.views.RoleViewSet, base_name='identity-role')
person_router.register('source-document', idm_core.attestation.views.SourceDocumentViewSet, base_name='identity-source-document')
person_router.register('name', idm_core.name.views.NameViewSet, base_name='identity-name')
person_router.register('identifier', idm_core.identifier.views.IdentifierViewSet, base_name='identity-identifier')
person_router.register('attestable', idm_core.attestation.views.AttestableViewSet, base_name='identity-attestable')


router.register('name', idm_core.name.views.NameViewSet)
router.register('nationality', idm_core.nationality.views.NationalityViewSet)
router.register('source-document', idm_core.attestation.views.SourceDocumentViewSet)
router.register('attestation', idm_core.attestation.views.AttestationViewSet)
router.register('affiliation', idm_core.relationship.views.AffiliationViewSet)
router.register('role', idm_core.relationship.views.RoleViewSet)
router.register('identifier', idm_core.identifier.views.IdentifierViewSet)
router.register('email', idm_core.contact.views.EmailViewSet)
router.register('telephone', idm_core.contact.views.TelephoneViewSet)
router.register('address', idm_core.contact.views.AddressViewSet)

admin.autodiscover()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(person_router.urls)),
    url(r'^admin/', admin.site.urls),

]
