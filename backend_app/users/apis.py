from django.http import JsonResponse, Http404
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser

from django_filters import rest_framework as filters
from organizations.models import Organization, OrganizationUser, OrganizationOwner
# from organizations.backends.tokens import RegistrationTokenGenerator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from common.utils import get_api_default_permissions
from common.utils.pagination import StandardResultsSetPagination
from common.utils.password import get_random_alphanumeric_string, get_random_int_string
from .serializers import OrganizationSerializer, OrganizationUserSerializer
from .serializers import OrganizationFilter, OrganizationUserFilter
from .serializers import UserSerializer
from .backends import InvitationBackend, CustomInvitations

import json


class UserSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        current_user = self.request.user

        # Check if user is admin or organizationowner
        if current_user.is_superuser:
            return get_user_model().objects.all().order_by('id')

        org_admins = []
        for org in current_user.organizations_organization.all():
            try:
                if org.is_owner(current_user) or org.is_admin(current_user):
                    org_admins.append(org)
            except Exception:
                pass

        return get_user_model().objects.filter(organizations_organization__in=org_admins).order_by('id')


class OrganizationUserSet(viewsets.ModelViewSet):
    serializer_class = OrganizationUserSerializer
    filterset_class = OrganizationUserFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        current_user = self.request.user

        # Check if user is admin or organizationowner
        if current_user.is_superuser:
            return OrganizationUser.objects.all().annotate(
                username=F('user__username'),
                email=F('user__email'),
                org_name=F('organization__name'),
            ).order_by('id')

        org_admins = []
        for org in current_user.organizations_organization.all():
            try:
                if org.is_owner(current_user) or org.is_admin(current_user):
                    org_admins.append(org)
            except Exception as e:
                print(e)
                pass
        return OrganizationUser.objects.filter(organization__in=org_admins).order_by('id')


class OrganizationSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        current_user = self.request.user

        # Check if user is admin or orgasationowner
        if current_user.is_superuser:
            return Organization.objects.all().order_by('name')

        # List organization which current_user is admin of
        org_admin = []
        for org in current_user.organizations_organization.all():
            if org.is_owner(current_user) or org.is_admin(current_user):
                org_admin.append(org.id)

        return current_user.organizations_organization.filter(id__in=org_admin, is_active=True).order_by('name')


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def activate_user(self, token):
    # token format: <user_id>-<user_token> (ex: 24-5ev-90e516079f1b118c410bh)
    #   user_id: 24
    #   user_token: 5ev-90e516079f1b118c410bh

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
    # if not RegistrationTokenGenerator().check_token(user, user_token):
    if not PasswordResetTokenGenerator().check_token(user, user_token):
        raise Http404(_("Your URL may have expired."))

    # Collect data from form
    data = self.data

    # Override static values
    data.update({
        'email': user.email,
        'profile': user.profile,
        'type': user.type,
        'created_at': user.created_at,
        'updated_at': timezone.now(),
    })
    form = InvitationBackend().get_form(
        data=data or None,
        # files=self.FILES or None,
        instance=user)
    if form.is_valid():
        try:
            form.instance.is_active = True
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            InvitationBackend().activate_organizations(user)

            # Create a personal organization, organization user & owner
            personal_org = Organization.objects.create(
                is_active=True,
                name="Private"
            )
            personal_org.save()
            personal_org.slug = "{}-{}".format(personal_org.slug, user.email)
            personal_org.save()

            personal_org_user = OrganizationUser.objects.create(
                user=user,
                organization=personal_org,
                is_admin=True)
            personal_org_user.save()

            personal_org_owner = OrganizationOwner.objects.create(
                organization=personal_org,
                organization_user=personal_org_user
            )
            personal_org_owner.save()

            return JsonResponse({'status': 'success'}, safe=False)
        except Exception as e:
            return JsonResponse({'status': 'error', 'reason': str(e)}, safe=False)
    return JsonResponse({'status': 'valid', 'email': user.email}, safe=False)


@api_view(['POST', 'PUT'])
@permission_classes((IsAdminUser, ))
def add_user(self):
    if not self.user.is_superuser:
        raise PermissionDenied(_("Sorry, admins only"))

    if not set(self.data.keys()).issubset(['username', 'email', 'password', 'type', 'profile']):
        return JsonResponse({
            'status': 'error',
            'reason': 'missing parameters'}, safe=False)
    try:

        username = "user_"
        if 'username' in self.data.keys():
            username = self.data['username']
        else:
            # Determine a random username
            username = 'user_'+get_random_int_string(10)
            while get_user_model().objects.filter(username=username):
                username = 'user_'+get_random_int_string(10)

        email = username+'@hears.patrowl.io'
        if 'email' in self.data.keys():
            email = self.data['email']

        password = get_random_alphanumeric_string(16)
        if 'password' in self.data.keys():
            password = self.data['password']

        user = get_user_model().objects.create_user(
            username,
            email,
            password
        )

        if 'first_name' in self.data.keys():
            user.first_name = self.data['first_name']
        if 'last_name' in self.data.keys():
            user.last_name = self.data['last_name']
        if 'profile' in self.data.keys():
            if type(self.data['profile']) == str:
                user.profile = json.loads(self.data['profile'])
            elif type(self.data['profile']) == dict:
                user.profile = self.data['profile']
        if 'type' in self.data.keys() and self.data['type'] in ['SAAS-API', 'SAAS-WEB', 'DEFAULT']:
            user.type = self.data['type']

        user.save()

        # Create an authtoken
        token = Token.objects.get_or_create(user=user)[0]

        # Create a default organization 'Private'
        org = Organization.objects.create(name='Private', is_active=True)
        org.save()
        org_user = OrganizationUser.objects.create(user=user, organization=org, is_admin=True)
        org_user.save()
        org_owner = OrganizationOwner.objects.create(organization=org, organization_user=org_user)
        org_owner.save()

        # Create a Team organization if had manage_organization
        if 'manage_organization' in user.profile.keys() and user.profile['manage_organization'] is True:
            team_org = Organization.objects.create(name='Team', is_active=True)
            team_org.save()
            team_org.org_settings.alerts_emails_enabled = user.profile['manage_alert_email']
            team_org.org_settings.alerts_slack_enabled = user.profile['manage_alert_slack']
            team_org.org_settings.max_users = int(user.profile['organization_users'])
            team_org.org_settings.save()
            team_org_user = OrganizationUser.objects.create(user=user, organization=team_org, is_admin=True)
            team_org_user.save()
            team_org_owner = OrganizationOwner.objects.create(organization=team_org, organization_user=team_org_user)
            team_org_owner.save()

        user_dict = user.to_dict()
        user_dict.update({'password': password})
        user_dict.update({'token': token.key})

        return JsonResponse({'status': 'success', 'user': user_dict}, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'reason': 'no'}, safe=False)


@api_view(['GET', 'DELETE'])
@permission_classes((IsAdminUser, ))
def delete_user(self, user_id):
    if not self.user.is_superuser:
        raise PermissionDenied(_("Sorry, admins only"))

    try:
        user = get_user_model().objects.get(id=user_id)
        user.organizations_organization.all().delete()
        user.delete()
        return JsonResponse({'status': 'success'}, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'reason': 'no'}, safe=False)


@api_view(['POST'])
def invite_user(self, organization_id):
    org = get_object_or_404(Organization, id=organization_id)

    # Check if user is allowed
    if self.user.is_superuser is False:
        if org.is_admin(self.user) is False:
            return JsonResponse({
                'status': 'error',
                'reason': 'Admin and Org admin allowed only.'}, safe=False)
        if settings.RESTRICTED_MODE is True and org.org_settings.max_users not in [-1, 'unlimited']:
            if org.organization_users.count() >= org.org_settings.max_users:
                return JsonResponse({
                    'status': 'error',
                    'reason': 'Max users reached. Upgrade your account if needed'}, safe=False)

    emails = self.data.getlist('emails', '')[0]
    for email in " ".join(emails.split()).replace(';', ',').replace(' ', ',').split(',')[:50]:
        if email not in [None, '']:
            print(email)
            try:
                try:
                    user = get_user_model().objects.get(email__iexact=email)
                except get_user_model().MultipleObjectsReturned:
                    return JsonResponse({
                        'status': 'error',
                        'reason': 'This email address has been used multiple times'}, safe=False)
                except get_user_model().DoesNotExist:
                    user = CustomInvitations().invite_by_email(
                            email,
                            **{
                                'organization': org,
                                'sender': self.user,
                                'BASE_URL': settings.BASE_URL
                            })
                # Send a notification email to this user to inform them that they
                # have been added to a new organization.
                CustomInvitations().send_notification(user, **{
                    'organization': org,
                    'sender': self.user,
                    'BASE_URL': settings.BASE_URL
                })
                org_user = OrganizationUser.objects.create(
                    user=user,
                    organization=org
                )
                org_user.save()
            except Exception:
                pass

    return JsonResponse({'status': 'success'}, safe=False)


@api_view(['POST'])
def update_user_profile(self):
    first_name = self.data.get('first_name', None)
    if first_name is not None:
        self.user.first_name = first_name

    last_name = self.data.get('last_name', None)
    if last_name is not None:
        self.user.last_name = last_name

    is_active = self.data.get('is_active', None)
    if is_active is not None:
        self.user.is_active = is_active.lower() in ['yes', 'true', 'y', '1', 'on']

    try:
        self.user.save()
        return JsonResponse({'status': 'success'}, safe=False)
    except Exception:
        return JsonResponse({'status': 'error'}, status=500, safe=False)


@api_view(['POST'])
@permission_classes((IsAdminUser, ))
def update_user_profile_admin(self, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    first_name = self.data.get('first_name', None)
    if first_name is not None:
        user.first_name = first_name

    last_name = self.data.get('last_name', None)
    if last_name is not None:
        user.last_name = last_name

    is_active = self.data.get('is_active', None)
    if is_active is not None:
        user.is_active = is_active.lower() in ['yes', 'true', 'y', '1', 'on']

    try:
        user.save()
        return JsonResponse({'status': 'success'}, safe=False)
    except Exception:
        return JsonResponse({'status': 'error'}, status=500, safe=False)


@api_view(['POST'])
def update_user_password(self):
    form = PasswordChangeForm(user=self.user, data=self.POST)
    if form.is_valid():
        form.save()
        update_session_auth_hash(self, form.user)
        return JsonResponse({'status': 'success'}, safe=False)
    return JsonResponse({'status': 'error'}, status=500, safe=False)


@api_view(['POST'])
@permission_classes((IsAdminUser, ))
def create_organization(self):
    if not self.user.is_superuser:
        raise PermissionDenied(_("Sorry, (org) admins only"))

    if set(['name', 'is_active', 'email']).issubset(self.data.keys()) is False:
        return JsonResponse("error.", safe=False, status=500)
    org_name = self.data.get('name')
    is_active = self.data.get('is_active', None) == "true"
    owner_email = self.data.get('email')

    # Create the new organization
    try:
        org = Organization.objects.create(name=org_name, is_active=is_active)
        org.save()
    except Exception:
        return JsonResponse("error.", safe=False, status=400)

        # Create or activate owner
    try:
        user = get_user_model().objects.get(email__iexact=owner_email)
    except get_user_model().MultipleObjectsReturned:
        raise Http404(_("This email address has been used multiple times."))
    except get_user_model().DoesNotExist:
        user = CustomInvitations().invite_by_email(
                owner_email,
                **{
                    'organization': org,
                    'sender': self.user,
                    'BASE_URL': settings.BASE_URL
                })
    # Send a notification email to this user to inform them that they
    # have been added to a new organization.
    CustomInvitations().send_notification(user, **{
        'organization': org,
        'sender': self.user,
        'BASE_URL': settings.BASE_URL
    })
    org_user = OrganizationUser.objects.create(
        user=user,
        organization=org,
        is_admin=True)
    org_user.save()

    org_owner = OrganizationOwner.objects.create(
        organization=org,
        organization_user=org_user
    )
    org_owner.save()

    return JsonResponse({'status': 'success'}, safe=False)


def check_float_in_range(value, min, max):
    if min <= value <= max and round(value, 2) == value:
        return True
    return False


@api_view(['POST'])
def update_org_settings(self):
    organization_id = self.data.get('org_id', None)
    org = get_object_or_404(Organization, id=organization_id)
    if not self.user.is_superuser and not org.is_admin(self.user):
        raise PermissionDenied(_("Sorry, (org) admins only"))

    # Alert settings
    alert_emails = self.data.get('alerts_emails', None)
    if alert_emails is not None:
        emails = []
        for e in alert_emails.split(','):
            if settings.HEARS_VALIDATE_EMAIL is False:
                emails.append(e)
                continue
            else:
                is_email_valid = False
                try:
                    if validate_email(e):
                        is_email_valid = True
                except ValidationError:
                    pass
                if is_email_valid:
                    emails.append(e)
        org.org_settings.alerts_emails = emails

    enable_email_alert_new_vuln = self.data.get('enable_email_alert_new_vuln', None)
    if enable_email_alert_new_vuln is not None and enable_email_alert_new_vuln in ["true", "false"]:
        org.org_settings.enable_email_alert_new_vuln = enable_email_alert_new_vuln == "true"

    enable_email_alert_update_vuln = self.data.get('enable_email_alert_update_vuln', None)
    if enable_email_alert_update_vuln is not None and enable_email_alert_update_vuln in ["true", "false"]:
        org.org_settings.enable_email_alert_update_vuln = enable_email_alert_update_vuln == "true"

    enable_daily_email_report = self.data.get('enable_daily_email_report', None)
    if enable_daily_email_report is not None and enable_daily_email_report in ["true", "false"]:
        org.org_settings.enable_daily_email_report = enable_daily_email_report == "true"

    enable_weekly_email_report = self.data.get('enable_weekly_email_report', None)
    if enable_weekly_email_report is not None and enable_weekly_email_report in ["true", "false"]:
        org.org_settings.enable_weekly_email_report = enable_weekly_email_report == "true"

    enable_monthly_email_report = self.data.get('enable_monthly_email_report', None)
    if enable_monthly_email_report is not None and enable_monthly_email_report in ["true", "false"]:
        org.org_settings.enable_monthly_email_report = enable_monthly_email_report == "true"

    enable_instant_email_report_exploitable = self.data.get('enable_instant_email_report_exploitable', None)
    if enable_instant_email_report_exploitable is not None and enable_instant_email_report_exploitable in ["true", "false"]:
        org.org_settings.enable_instant_email_report_exploitable = enable_instant_email_report_exploitable == "true"

    enable_instant_email_report_cvss = self.data.get('enable_instant_email_report_cvss', None)
    if enable_instant_email_report_cvss is not None and enable_instant_email_report_cvss in ["true", "false"]:
        org.org_settings.enable_instant_email_report_cvss = enable_instant_email_report_cvss == "true"

    enable_instant_email_report_cvss_value = self.data.get('enable_instant_email_report_cvss_value', None)
    if enable_instant_email_report_cvss_value is not None and check_float_in_range(float(enable_instant_email_report_cvss_value), 0.0, 10):
        org.org_settings.enable_instant_email_report_cvss_value = float(enable_instant_email_report_cvss_value)

    enable_instant_email_report_cvss3 = self.data.get('enable_instant_email_report_cvss3', None)
    if enable_instant_email_report_cvss3 is not None and enable_instant_email_report_cvss3 in ["true", "false"]:
        org.org_settings.enable_instant_email_report_cvss3 = enable_instant_email_report_cvss3 == "true"
    else:
        org.org_settings.enable_instant_email_report_cvss3 = False

    enable_instant_email_report_cvss3_value = self.data.get('enable_instant_email_report_cvss3_value', None)
    if enable_instant_email_report_cvss3_value is not None and check_float_in_range(float(enable_instant_email_report_cvss3_value), 0.0, 10):
        org.org_settings.enable_instant_email_report_cvss3_value = float(enable_instant_email_report_cvss3_value)
    else:
        org.org_settings.enable_instant_email_report_cvss3_value = 10

    enable_instant_email_report_score = self.data.get('enable_instant_email_report_score', None)
    if enable_instant_email_report_score is not None and enable_instant_email_report_score in ["true", "false"]:
        org.org_settings.enable_instant_email_report_score = enable_instant_email_report_score == "true"

    enable_instant_email_report_score_value = self.data.get('enable_instant_email_report_score_value', None)
    if enable_instant_email_report_score_value is not None and str(enable_instant_email_report_score_value).isnumeric() and 0 <= int(enable_instant_email_report_score_value) <= 100:
        org.org_settings.enable_instant_email_report_score_value = int(enable_instant_email_report_score_value)

    # Slack
    enable_slack_new_vuln = self.data.get('enable_slack_new_vuln', None)
    if enable_slack_new_vuln is not None and enable_slack_new_vuln in ["true", "false"]:
        org.org_settings.alerts_slack['new_vuln'] = enable_slack_new_vuln == "true"

    enable_slack_update_vuln = self.data.get('enable_slack_update_vuln', None)
    if enable_slack_update_vuln is not None and enable_slack_update_vuln in ["true", "false"]:
        org.org_settings.alerts_slack['update_vuln'] = enable_slack_update_vuln == "true"

    alerts_slack_url = self.data.get('alerts_slack_url', None)
    if alerts_slack_url is not None:
        org.org_settings.alerts_slack['url'] = alerts_slack_url

    # TheHive
    enable_thehive_new_vuln = self.data.get('enable_thehive_new_vuln', None)
    if enable_thehive_new_vuln is not None and enable_thehive_new_vuln in ["true", "false"]:
        org.org_settings.alerts_thehive['new_vuln'] = enable_thehive_new_vuln == "true"

    enable_thehive_update_vuln = self.data.get('enable_thehive_update_vuln', None)
    if enable_thehive_update_vuln is not None and enable_thehive_update_vuln in ["true", "false"]:
        org.org_settings.alerts_thehive['update_vuln'] = enable_thehive_update_vuln == "true"

    alerts_thehive_url = self.data.get('alerts_thehive_url', None)
    if alerts_thehive_url is not None:
        org.org_settings.alerts_thehive['url'] = alerts_thehive_url

    alerts_thehive_apikey = self.data.get('alerts_thehive_apikey', None)
    if alerts_thehive_apikey is not None:
        org.org_settings.alerts_thehive['apikey'] = alerts_thehive_apikey

    # MISP
    enable_misp_new_vuln = self.data.get('enable_misp_new_vuln', None)
    if enable_misp_new_vuln is not None and enable_misp_new_vuln in ["true", "false"]:
        org.org_settings.alerts_misp['new_vuln'] = enable_misp_new_vuln == "true"

    enable_misp_update_vuln = self.data.get('enable_misp_update_vuln', None)
    if enable_misp_update_vuln is not None and enable_misp_update_vuln in ["true", "false"]:
        org.org_settings.alerts_misp['update_vuln'] = enable_misp_update_vuln == "true"

    alerts_misp_url = self.data.get('alerts_misp_url', None)
    if alerts_misp_url is not None:
        org.org_settings.alerts_misp['url'] = alerts_misp_url

    alerts_misp_apikey = self.data.get('alerts_misp_apikey', None)
    if alerts_misp_apikey is not None:
        org.org_settings.alerts_misp['apikey'] = alerts_misp_apikey

    org.org_settings.save()
    return JsonResponse({
        'status': 'success',
        'alerts_emails': org.org_settings.alerts_emails,
        'enable_email_alert_new_vuln': org.org_settings.enable_email_alert_new_vuln,
        'enable_email_alert_update_vuln': org.org_settings.enable_email_alert_update_vuln,
        'enable_daily_email_report': org.org_settings.enable_daily_email_report,
        'enable_weekly_email_report': org.org_settings.enable_weekly_email_report,
        'enable_monthly_email_report': org.org_settings.enable_monthly_email_report,
        'enable_instant_email_report_exploitable': org.org_settings.enable_instant_email_report_exploitable,
        'enable_instant_email_report_score': org.org_settings.enable_instant_email_report_score,
        'enable_instant_email_report_score_value': org.org_settings.enable_instant_email_report_score_value,
        'enable_instant_email_report_cvss': org.org_settings.enable_instant_email_report_cvss,
        'enable_instant_email_report_cvss_value': org.org_settings.enable_instant_email_report_cvss_value,
        'enable_instant_email_report_cvss3': org.org_settings.enable_instant_email_report_cvss3,
        'enable_instant_email_report_cvss3_value': org.org_settings.enable_instant_email_report_cvss3_value,
        'enable_slack_new_vuln': org.org_settings.alerts_slack['new_vuln'],
        'enable_slack_update_vuln': org.org_settings.alerts_slack['update_vuln'],
        'alerts_slack_url': org.org_settings.alerts_slack['url'],
        'enable_thehive_new_vuln': org.org_settings.alerts_thehive['new_vuln'],
        'enable_thehive_update_vuln': org.org_settings.alerts_thehive['update_vuln'],
        'alerts_thehive_url': org.org_settings.alerts_thehive['url'],
        'alerts_thehive_apikey': org.org_settings.alerts_thehive['apikey'],
        'enable_misp_new_vuln': org.org_settings.alerts_misp['new_vuln'],
        'enable_misp_update_vuln': org.org_settings.alerts_misp['update_vuln'],
        'alerts_misp_url': org.org_settings.alerts_misp['url'],
        'alerts_misp_apikey': org.org_settings.alerts_misp['apikey'],
    }, safe=False)


@api_view(['GET'])
def disable_org(self, organization_id):
    org = get_object_or_404(Organization, id=organization_id)
    if not self.user.is_superuser and not org.is_admin(self.user):
        raise PermissionDenied(_("Sorry, (org) admins only"))
    org.is_active = False
    org.save()
    return JsonResponse({'status': 'disabled'}, safe=False)


@api_view(['GET'])
def enable_org(self, organization_id):
    org = get_object_or_404(Organization, id=organization_id)
    if not self.user.is_superuser and not org.is_admin(self.user):
        raise PermissionDenied(_("Sorry, (org) admins only"))
    org.is_active = True
    org.save()
    return JsonResponse({'status': 'enabled'}, safe=False)


@api_view(['GET'])
def enable_admin_org(self, org_id, user_id):
    org = get_object_or_404(Organization, id=org_id)
    if not self.user.is_superuser and not org.is_admin(self.user):
        raise PermissionDenied(_("Sorry, (org) admins only"))
    user = get_object_or_404(OrganizationUser, organization_id=org_id, user_id=user_id)
    user.is_admin = True
    user.save()
    return JsonResponse({'status': 'enabled'}, safe=False)


@api_view(['GET'])
def disable_admin_org(self, org_id, user_id):
    org = get_object_or_404(Organization, id=org_id)
    if not self.user.is_superuser and not org.is_admin(self.user):
        raise PermissionDenied(_("Sorry, (org) admins only"))
    user = get_object_or_404(OrganizationUser, organization_id=org_id, user_id=user_id)
    user.is_admin = False
    user.save()
    return JsonResponse({'status': 'disabled'}, safe=False)


@api_view(['GET'])
def remove_user_from_org(self, org_id, user_id):
    org = get_object_or_404(Organization, id=org_id)
    if not self.user.is_superuser and not org.is_admin(self.user):
        raise PermissionDenied(_("Sorry, (org) admins only"))

    # Delete organization if there is only one remaining user
    if org.users.count() == 1:
        org.delete()
    else:
        user = get_object_or_404(OrganizationUser, organization_id=org_id, user_id=user_id)
        user.delete()
    return JsonResponse({'status': 'removed'}, safe=False)


@api_view(['GET'])
def remove_org(self, organization_id):
    org = get_object_or_404(Organization, id=organization_id)
    if not self.user.is_superuser:
        raise PermissionDenied(_("Sorry, (org) admins only"))
    org.delete()
    return JsonResponse({'status': 'removed'}, safe=False)


@api_view(['GET'])
def set_org(self, org_id):
    user = None
    if self.user.is_superuser:
        user = OrganizationUser.objects.all().first()
        org = get_object_or_404(Organization, id=org_id)
    else:
        user = get_object_or_404(OrganizationUser, organization_id=org_id, user_id=self.user.id)
        org = user.organization
    self.session['org_id'] = org.id
    self.session['org_name'] = org.name
    return JsonResponse({
        'status': 'set',
        'org_id': org.id,
        'org_name': org.name
        },
        safe=False
    )


@api_view(['GET'])
def set_default_org(self):
    user = None
    if self.user.is_superuser:
        user = OrganizationUser.objects.all().first()
    else:
        user = OrganizationUser.objects.filter(user_id=self.user.id, organization__is_active=True).first()
        
    self.session['org_id'] = user.organization.id
    self.session['org_name'] = user.organization.name
    return JsonResponse({
        'status': 'set',
        'org_id': user.organization.id,
        'org_name': user.organization.name
        }, safe=False
    )


@api_view(['GET'])
def get_org_settings(self, org_id):
    user = None
    if self.user.is_superuser:
        user = OrganizationUser.objects.all().first()
        org = get_object_or_404(Organization, id=org_id)
    else:
        user = get_object_or_404(OrganizationUser, organization_id=org_id, user_id=self.user.id)
        org = user.organization

    return JsonResponse({
        'org_id': org.id,
        'org_name': org.name,
        'alerts_emails': org.org_settings.alerts_emails,
        'alerts_emails_enabled': org.org_settings.alerts_emails_enabled,
        'enable_email_alert_new_vuln': org.org_settings.enable_email_alert_new_vuln,
        'enable_email_alert_update_vuln': org.org_settings.enable_email_alert_update_vuln,
        'enable_daily_email_report': org.org_settings.enable_daily_email_report,
        'enable_weekly_email_report': org.org_settings.enable_weekly_email_report,
        'enable_monthly_email_report': org.org_settings.enable_monthly_email_report,
        'enable_instant_email_report_exploitable': org.org_settings.enable_instant_email_report_exploitable,
        'enable_instant_email_report_score': org.org_settings.enable_instant_email_report_score,
        'enable_instant_email_report_score_value': org.org_settings.enable_instant_email_report_score_value,
        'enable_instant_email_report_cvss': org.org_settings.enable_instant_email_report_cvss,
        'enable_instant_email_report_cvss_value': org.org_settings.enable_instant_email_report_cvss_value,
        'alerts_slack': org.org_settings.alerts_slack,
        'alerts_slack_enabled': org.org_settings.alerts_slack_enabled,
        'alerts_thehive': org.org_settings.alerts_thehive,
        'alerts_thehive_enabled': org.org_settings.alerts_thehive_enabled,
        'alerts_misp': org.org_settings.alerts_misp,
        'alerts_misp_enabled': org.org_settings.alerts_misp_enabled,
    }, safe=False)


# Auth token management
@api_view(['GET'])
def get_curruser_authtoken(request):
    try:
        token = Token.objects.filter(user=request.user).first()
        return JsonResponse({"status": "success", "token": token.key})
    except Exception:
        pass
    return JsonResponse({
        "status": "error",
        "reason": "Unable to retrieve user's token"})


@api_view(['GET'])
def get_user_authtoken(request, user_id):
    try:
        uid = get_object_or_404(get_user_model(), id=user_id)
        token = Token.objects.filter(user=uid).first()
        return JsonResponse({"status": "success", "token": token.key})
    except Exception:
        pass
    return JsonResponse({
        "status": "error",
        "reason": "Unable to retrieve user's token"})


@api_view(['GET'])
def delete_curruser_authtoken(request):
    try:
        for token in Token.objects.filter(user=request.user):
            token.delete()
        return JsonResponse({"status": "success"})
    except Exception:
        pass
    return JsonResponse({
        "status": "error",
        "reason": "Unable to delete user's token"})


@api_view(['GET'])
def delete_user_authtoken(request, user_id):
    try:
        uid = get_object_or_404(get_user_model(), id=user_id)
        for token in Token.objects.filter(user=uid):
            token.delete()
        return JsonResponse({"status": "success"})
    except Exception:
        pass
    return JsonResponse({
        "status": "error",
        "reason": "Unable to delete user's token"})


@api_view(['GET'])
def renew_curruser_authtoken(request):
    try:
        for token in Token.objects.filter(user=request.user):
            token.delete()
        token = Token.objects.get_or_create(user=request.user)[0]
        return JsonResponse({"status": "success", "token": token.key})
    except Exception:
        pass
    return JsonResponse({
        "status": "error",
        "reason": "Unable to renew user's token"})


@api_view(['GET'])
def renew_user_authtoken(request, user_id):
    try:
        uid = get_object_or_404(get_user_model(), id=user_id)
        for token in Token.objects.filter(user=uid):
            token.delete()
        token = Token.objects.get_or_create(user=uid)[0]
        return JsonResponse({"status": "success", "token": token.key})
    except Exception:
        pass
    return JsonResponse({
        "status": "error",
        "reason": "Unable to renew user's token"})


@api_view(['GET'])
def renew_user_password(request, user_id):
    if not request.user.is_superuser:
        #@Todo: check if current user is a related org admin
        raise PermissionDenied(_("Sorry, admins only"))

    try:
        user = get_object_or_404(get_user_model(), id=user_id)
        new_password = get_random_alphanumeric_string(16)
        user.set_password(new_password)
        user.save()
        return JsonResponse({"status": "success", "password": new_password})
    except Exception:
        pass
    return JsonResponse({
        "status": "error",
        "reason": "Unable to renew user's password"})
