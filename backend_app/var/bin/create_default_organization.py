from organizations.models import Organization, OrganizationUser, OrganizationOwner
from django.contrib.auth import get_user_model
admin_user = get_user_model().objects.get(username='admin')
if admin_user.organizations_organization.count() == 0:
    admin_org = Organization.objects.create(name='Private', is_active=True)
    admin_org.save()
    org_user = OrganizationUser.objects.create(user=admin_user, organization=admin_org, is_admin=True)
    org_user.save()
    org_owner = OrganizationOwner.objects.create(organization=admin_org, organization_user=org_user)
    org_owner.save()
