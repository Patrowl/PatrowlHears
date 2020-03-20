# -*- coding: utf-8 -*-

from rest_framework import serializers, generics, views, response, permissions
# from django_filters import rest_framework as filters
from django_filters import FilterSet, OrderingFilter, CharFilter
from django.utils.translation import gettext_lazy as _
from organizations.models import OrganizationUser, Organization, OrganizationOwner
from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_org_admin = serializers.SerializerMethodField()

    def get_is_org_admin(self, instance):
        is_org_admin = False
        if OrganizationUser.objects.filter(user_id=instance.id, is_admin=True).count() > 0:
            is_org_admin = True
        return is_org_admin

    class Meta:
        model = User
        fields = ('id', 'username', 'last_login', 'is_superuser', 'is_staff', 'is_org_admin')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CurrentUserView(views.APIView):

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return response.Response(serializer.data)


class OrganizationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'is_active']
        datatables_always_serialize = ['id']


class OrganizationFilter(FilterSet):

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('name', _('Organization Name')), ('-name', _('Organization Name (Desc)')),
        )
    )

    # class Meta:
    #     model = OrganizationUser
    #     fields = {
    #         'name': ['icontains'],
    #         # 'vuln_id': ['exact'],
    #     }


class OrganizationUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    org_id = serializers.SerializerMethodField()
    org_name = serializers.SerializerMethodField()

    def get_username(self, instance):
        return instance.user.username

    def get_email(self, instance):
        return instance.user.email

    def get_org_id(self, instance):
        return instance.organization.id

    def get_org_name(self, instance):
        return instance.organization.name

    class Meta:
        model = OrganizationUser
        fields = [
            'id', 'organization', 'user', 'username', 'email', 'is_admin',
            'org_id', 'org_name'
        ]
        datatables_always_serialize = ['id']


class OrganizationUserFilter(FilterSet):
    username = CharFilter(method='filter_username', field_name='product')

    def filter_username(self,  queryset, name, value):
        return queryset

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('username', _('Username')), ('-username', _('Username (Desc)')),
            ('email', _('Email')), ('-email', _('Email (Desc)')),
            ('org_name', _('Organization Name')), ('-org_name', _('Organization Name (Desc)')),
            ('is_admin', _('Is Admin')), ('-is_admin', _('Is Admin (Desc)')),
        )
    )

    class Meta:
        model = OrganizationUser
        fields = {
            'organization': ['exact'],
            # 'vuln_id': ['exact'],
        }
