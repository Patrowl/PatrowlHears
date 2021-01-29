from organizations.models import OrganizationUser, Organization


def get_current_organization(user, org_id=None):
    org = None
    # Admin
    if user.is_superuser:
        if org_id is None:
            org = Organization.objects.first()
        else:
            org = Organization.objects.get(id=org_id)
    else:
        # standard user
        _org = OrganizationUser.objects.filter(user_id=user.id, organization_id=org_id).first()
        if _org is not None:
            org = OrganizationUser.objects.get(user_id=user.id, organization_id=org_id).organization
        else:
            # Check if there is a Private one
            private_org = user.organizations_organization.filter(name='Private').first()
            if private_org is not None:
                org = private_org
            else:
                org = None
        # print(user.organizations_organizationuser.values('organization_id'))
        # print(user.organizations.filter(user_id=user.id))
        # org = user.organizations_organizationuser.filter(organization_id=org_id, organization__is_active=True).first()
    return org
