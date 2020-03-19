from django.http import JsonResponse, Http404
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model, authenticate, login
from django.db.models import F
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django_filters import rest_framework as filters
from organizations.models import Organization, OrganizationUser
from organizations.backends.tokens import RegistrationTokenGenerator
from common.utils.pagination import StandardResultsSetPagination
from .serializers import OrganizationSerializer, OrganizationUserSerializer
from .serializers import OrganizationFilter, OrganizationUserFilter
from .backends import InvitationBackend


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
            if org.is_owner(current_user):
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

        return current_user.organizations_organization.filter(is_active=True).order_by('name')


@api_view(['GET', 'POST'])
def activate_user(self, token):
    # token: 24-5ev-90e516079f1b118c410bh
    #   user_id: 24
    #   user_token: 5ev-90e516079f1b118c410bh
    try:
        user_id = token.split('-')[0]
        user_token = "-".join(token.split('-')[1:])
    except Exception:
        raise Http404(_("Bad Token"))
    try:
        user = get_user_model().objects.get(id=user_id, is_active=False)
    except get_user_model().DoesNotExist:
        raise Http404(_("Your URL may have expired."))
    if not RegistrationTokenGenerator().check_token(user, user_token):
        raise Http404(_("Your URL may have expired."))
    form = InvitationBackend().get_form(data=self.data or None, files=self.FILES or None, instance=user)
    if form.is_valid():
        form.instance.is_active = True
        user = form.save()
        user.set_password(form.cleaned_data['password'])
        user.save()
        InvitationBackend().activate_organizations(user)
        user = authenticate(username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
        login(self, user)
        return JsonResponse({'status': 'success'}, safe=False)
    return JsonResponse({'status': 'valid', 'email': user.email}, safe=False)
