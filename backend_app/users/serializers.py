# -*- coding: utf-8 -*-
from django.db.models import F
from rest_framework import serializers, views, response
from django_filters import FilterSet, OrderingFilter, CharFilter
from django.utils.translation import gettext_lazy as _
from organizations.models import OrganizationUser, Organization
from common.utils import organization
from django.contrib.auth import get_user_model
from .models import OrgSettings


class UserSerializer(serializers.ModelSerializer):
    orgs = serializers.SerializerMethodField()
    current_org = serializers.SerializerMethodField()
    is_org_admin = serializers.SerializerMethodField()

    def get_orgs(self, instance):
        if instance.is_superuser:
            return Organization.objects.all().values('id', 'name', 'slug')
        else:
            return instance.organizations_organization.filter(is_active=True).values('id', 'name', 'slug')

    def get_current_org(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        if org is not None:
            return {
                'org_id': org.id,
                'org_name': org.name
            }
        else:
            return {
                'org_id': None,
                'org_name': '-'
            }

    def get_is_org_admin(self, instance):
        is_org_admin = False
        if OrganizationUser.objects.filter(user_id=instance.id, is_admin=True).count() > 0:
            is_org_admin = True
        return is_org_admin

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
            'last_login', 'is_superuser', 'is_staff', 'is_active',
            'orgs', 'current_org', 'is_org_admin',
            'auth_token', 'profile')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CurrentUserView(views.APIView):
    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return response.Response(serializer.data)


class OrgSettingsSerializer(serializers.ModelSerializer):
    alerts_emails_enabled = serializers.SerializerMethodField()
    alerts_emails = serializers.SerializerMethodField()
    enable_email_alert_new_vuln = serializers.SerializerMethodField()
    enable_email_alert_update_vuln = serializers.SerializerMethodField()
    enable_daily_email_report = serializers.SerializerMethodField()
    enable_weekly_email_report = serializers.SerializerMethodField()
    enable_monthly_email_report = serializers.SerializerMethodField()
    alerts_slack = serializers.SerializerMethodField()
    alerts_slack_enabled = serializers.SerializerMethodField()
    alerts_thehive = serializers.SerializerMethodField()
    alerts_thehive_enabled = serializers.SerializerMethodField()
    alerts_misp = serializers.SerializerMethodField()
    alerts_misp_enabled = serializers.SerializerMethodField()

    def get_alerts_emails_enabled(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.alerts_emails_enabled

    def get_alerts_emails(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.alerts_emails

    def get_enable_email_alert_new_vuln(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.enable_email_alert_new_vuln

    def get_enable_email_alert_update_vuln(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.enable_email_alert_update_vuln

    def get_enable_daily_email_report(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.enable_daily_email_report

    def get_enable_weekly_email_report(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.enable_weekly_email_report

    def get_enable_monthly_email_report(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.enable_monthly_email_report

    def get_alerts_slack(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.alerts_slack

    def get_alerts_slack_enabled(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.alerts_slack_enabled

    def get_alerts_thehive(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.alerts_thehive

    def get_alerts_thehive_enabled(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.alerts_thehive_enabled

    def get_alerts_misp(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.alerts_misp

    def get_alerts_misp_enabled(self, instance):
        org_id = self.context.get('request').session.get('org_id', None)
        if org_id is None:
            return {}
        org = organization.get_current_organization(user=instance, org_id=org_id)
        return org.org_settings.alerts_misp_enabled

    class Meta:
        model = OrgSettings
        fields = (
            'alerts_emails',
            'alerts_emails_enabled',
            'enable_email_alert_new_vuln',
            'enable_email_alert_update_vuln',
            'enable_daily_email_report',
            'enable_weekly_email_report',
            'enable_monthly_email_report',
            'alerts_slack',
            'alerts_slack_enabled',
            'alerts_thehive',
            'alerts_thehive_enabled',
            'alerts_misp',
            'alerts_misp_enabled',
        )


class OrgSettingsView(views.APIView):
    def get(self, request):
        serializer = OrgSettingsSerializer(request.user, context={'request': request})
        return response.Response(serializer.data)


class OrganizationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    owner = serializers.SerializerMethodField()
    nb_users = serializers.SerializerMethodField()

    def get_owner(self, instance):
        owner = "-/-"
        if hasattr(instance, 'owner'):
            owner = "{}/{}".format(instance.owner.organization_user.user.username, instance.owner.organization_user.user.email)
        return owner

    def get_nb_users(self, instance):
        return instance.organization_users.count()

    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'is_active', 'owner', 'nb_users']
        datatables_always_serialize = ['id']


class OrganizationFilter(FilterSet):
    owner = CharFilter(method='filter_owner', field_name='owner')

    def filter_owner(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(owner=F('id')).filter(owner=value)
        return queryset

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('name', _('Organization Name')), ('-name', _('Organization Name (Desc)')),
            ('slug', _('Slug')), ('-slug', _('Slug (Desc)')),
            ('owner', _('Owner')), ('-owner', _('Owner (Desc)')),
        )
    )


class OrganizationUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    org_id = serializers.SerializerMethodField()
    org_name = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    def get_username(self, instance):
        return instance.user.username

    def get_email(self, instance):
        return instance.user.email

    def get_org_id(self, instance):
        return instance.organization.id

    def get_org_name(self, instance):
        return instance.organization.name

    def get_is_active(self, instance):
        return instance.user.is_active

    class Meta:
        model = OrganizationUser
        fields = [
            'id', 'organization', 'user', 'username', 'email',
            'is_admin', 'is_active',
            'org_id', 'org_name'
        ]
        datatables_always_serialize = ['id']


class OrganizationUserOrderingFilter(OrderingFilter):
    def filter(self, qs, value):
        if value is None or len(value) == 0:
            return super(OrganizationUserOrderingFilter, self).filter(qs, value)
        if value[0] == 'username':
            qs = qs.annotate(username=F('user__username')).order_by('username')
        if value[0] == '-username':
            qs = qs.annotate(username=F('user__username')).order_by('-username')
        if value[0] == 'email':
            qs = qs.annotate(email=F('user__email')).order_by('email')
        if value[0] == '-email':
            qs = qs.annotate(email=F('user__email')).order_by('-email')
        if value[0] == 'emis_activeail':
            qs = qs.annotate(is_active=F('user__is_active')).order_by('is_active')
        if value[0] == '-is_active':
            qs = qs.annotate(is_active=F('user__is_active')).order_by('-is_active')
        if value[0] == 'org_name':
            qs = qs.annotate(org_name=F('organization__name')).order_by('org_name')
        if value[0] == '-org_name':
            qs = qs.annotate(org_name=F('organization__name')).order_by('-org_name')
        return super(OrganizationUserOrderingFilter, self).filter(qs, value)


class OrganizationUserFilter(FilterSet):
    username = CharFilter(method='filter_username', field_name='username')

    def filter_username(self,  queryset, name, value):
        if value:
            queryset = queryset.annotate(username=F('user__username')).filter(username=value)
        return queryset

    sorted_by = OrganizationUserOrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('username', _('Username')), ('-username', _('Username (Desc)')),
            ('email', _('Email')), ('-email', _('Email (Desc)')),
            ('org_name', _('Organization Name')), ('-org_name', _('Organization Name (Desc)')),
            ('is_admin', _('Is Admin')), ('-is_admin', _('Is Admin (Desc)')),
            ('is_active', _('Is Active')), ('-is_active', _('Is Active (Desc)')),
        )
    )

    class Meta:
        model = OrganizationUser
        # fields = {
        #     'organization': ['exact'],
        #     # 'vuln_id': ['exact'],
        # }
        fields = ['organization', 'username', 'is_admin']
        # fields = ['org_name', 'username', 'email', 'is_admin']

#
# class UserMonitoringListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = UserMonitoringList
#         fields = [
#             'id', 'user', 'vulns', 'products'
#         ]
#         datatables_always_serialize = ['id']
#
#
# class UserMonitoringListFilter(FilterSet):
#     # username = CharFilter(method='filter_username', field_name='product')
#     #
#     # def filter_username(self,  queryset, name, value):
#     #     return queryset
#
#     sorted_by = OrderingFilter(
#         choices=(
#             ('id', _('ID')), ('-id', _('ID (Desc)')),
#             # ('username', _('Username')), ('-username', _('Username (Desc)')),
#             # ('email', _('Email')), ('-email', _('Email (Desc)')),
#             # ('org_name', _('Organization Name')), ('-org_name', _('Organization Name (Desc)')),
#             # ('is_admin', _('Is Admin')), ('-is_admin', _('Is Admin (Desc)')),
#         )
#     )
#
#     class Meta:
#         model = UserMonitoringList
#         fields = {
#             'user': ['exact'],
#             # 'vuln_id': ['exact'],
#         }
