from organizations.models import OrganizationUser, Organization


def get_current_organization(user, org_id=None):
    org = None
    if user.is_superuser:
        if org_id is None:
            org = Organization.objects.first()
        else:
            org = Organization.objects.get(id=org_id)
    else:
        org = OrganizationUser.objects.get(user_id=user.id, organization_id=org_id).organization
    return org
