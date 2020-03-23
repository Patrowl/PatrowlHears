from django.http import JsonResponse, Http404
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model, authenticate, login
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
# from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django_filters import rest_framework as filters
from organizations.models import Organization, OrganizationUser
from organizations.views import BaseOrganizationUserCreate
from organizations.backends.tokens import RegistrationTokenGenerator
from common.utils.pagination import StandardResultsSetPagination
from .serializers import OrganizationSerializer, OrganizationUserSerializer
from .serializers import OrganizationFilter, OrganizationUserFilter
from .backends import InvitationBackend
from .mixins import OrganizationAdminOnly
from .models import UserMonitoringList


class OrganizationUserSet(viewsets.ModelViewSet):

    serializer_class = OrganizationUserSerializer
    filterset_class = OrganizationUserFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        current_user = self.request.user

        # Check if user is admin or orgasationowner
        if current_user.is_superuser:
            return OrganizationUser.objects.all().annotate(
                username=F('user__username'),
                email=F('user__email'),
                org_name=F('organization__name'),
            ).order_by('id')

        org_admins = []
        for org in Organization.objects.all():
            if org.is_owner(current_user) or org.is_admin(current_user):
                org_admins.append(org)
        return OrganizationUser.objects.filter(organization__in=org_admins).order_by('id')


class OrganizationSet(viewsets.ModelViewSet):

    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        current_user = self.request.user

        # Check if user is admin or orgasationowner
        if current_user.is_superuser:
            return Organization.objects.all().order_by('name')

        # List organization which current_user is admin of
        org_admin = []
        for org in Organization.objects.all():
            if org.is_owner(current_user) or org.is_admin(current_user):
                org_admin.append(org.id)

        return current_user.organizations_organization.filter(id__in=org_admin, is_active=True).order_by('name')
#
#
# class UserMonitoringListSet(viewsets.ModelViewSet):
#
#     # serializer_class = OrganizationSerializer
#     # filterset_class = OrganizationFilter
#     queryset = UserMonitoringList.objects.all()
#     filter_backends = (filters.DjangoFilterBackend,)
#     pagination_class = StandardResultsSetPagination
#
#     # def get_queryset(self):
#     #     current_user = self.request.user
#     #
#     #     # Check if user is admin or orgasationowner
#     #     if current_user.is_superuser:
#     #         return Organization.objects.all().order_by('name')
#     #
#     #     # List organization which current_user is admin of
#     #     org_admin = []
#     #     for org in Organization.objects.all():
#     #         if org.is_owner(current_user) or org.is_admin(current_user):
#     #             org_admin.append(org.id)
#     #
#     #     return current_user.organizations_organization.filter(id__in=org_admin, is_active=True).order_by('name')


@api_view(['GET', 'POST'])
def activate_user(self, token):
    # token format: <user_id>-<user_token> (ex: 24-5ev-90e516079f1b118c410bh)
    #   user_id: 24
    #   user_token: 5ev-90e516079f1b118c410bh

    print(self.data)
    # Check token format
    try:
        user_id = token.split('-')[0]
        user_token = "-".join(token.split('-')[1:])
    except Exception:
        raise Http404(_("Bad Token"))

    # Check user and token validity
    try:
        user = get_user_model().objects.get(id=user_id, is_active=False)
    except get_user_model().DoesNotExist:
        raise Http404(_("Your URL may have expired."))
    if not RegistrationTokenGenerator().check_token(user, user_token):
        raise Http404(_("Your URL may have expired."))

    # Collect data from form
    form = InvitationBackend().get_form(
        data=self.data or None,
        files=self.FILES or None,
        instance=user)
    if form.is_valid():
        form.instance.is_active = True
        user = form.save()
        user.set_password(form.cleaned_data['password'])
        user.save()
        InvitationBackend().activate_organizations(user)

        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'])
        login(self, user)
        return JsonResponse({'status': 'success'}, safe=False)
    return JsonResponse({'status': 'valid', 'email': user.email}, safe=False)


@api_view(['GET'])
def remove_user_from_org(self, org_id, user_id):
    org = get_object_or_404(Organization, id=org_id)
    if not self.user.is_superuser and not org.is_admin(self.user):
        raise PermissionDenied(_("Sorry, (org) admins only"))
    user = get_object_or_404(OrganizationUser, organization_id=org_id, user_id=user_id)
    user.delete()
    return JsonResponse({'status': 'removed'}, safe=False)


@api_view(['GET'])
def set_org(self, org_id):
    user = None
    if self.user.is_superuser:
        user = OrganizationUser.objects.all().first()
    else:
        user = get_object_or_404(OrganizationUser, organization_id=org_id, user_id=self.user.id)
    self.session['org_id'] = user.organization.id
    self.session['org_name'] = user.organization.name
    return JsonResponse({
        'status': 'set',
        'org_id': user.organization.id,
        'org_name': user.organization.name
        }, safe=False)


@api_view(['GET'])
def set_default_org(self):
    user = None
    if self.user.is_superuser:
        user = OrganizationUser.objects.all().first()
    else:
        user = OrganizationUser.objects.filter(user_id=self.user.id).first()
    self.session['org_id'] = user.organization.id
    self.session['org_name'] = user.organization.name
    return JsonResponse({
        'status': 'set',
        'org_id': user.organization.id,
        'org_name': user.organization.name
        }, safe=False)


class CustOrganizationUserCreate(OrganizationAdminOnly, BaseOrganizationUserCreate):
    """Override OrganizationUserCreate class using custom OrganizationAdminOnly."""
    pass
