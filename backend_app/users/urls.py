# -*- coding: utf-8 -*-
from django.urls import path
from . import serializers, apis

# Base URL: /api/users/
urlpatterns = [
    path('api/current', serializers.CurrentUserView.as_view()),
    path('profile', serializers.CurrentUserView.as_view()),
    path('profile/add', apis.add_user, name='add_user'),
    path('profile/del/<user_id>', apis.delete_user, name='delete_user'),
    path('profile/update', apis.update_user_profile, name='update_user_profile'),
    path('profile/chpwd', apis.update_user_password, name='update_user_password'),
    path('profile/<user_id>/renewpassword', apis.renew_user_password, name='renew_user_password'),
    path('profile/<user_id>/update', apis.update_user_profile_admin, name='update_user_profile_admin'),
    path('activate/<token>', apis.activate_user, name='activate_user'),
    path('set-org', apis.set_default_org, name='set_default_organization'),
    path('set-org/<org_id>', apis.set_org, name='set_organization'),
    path('org/info', serializers.OrgSettingsView.as_view()),
    path('org/<org_id>/settings', apis.get_org_settings, name='get_org_settings'),
    path('org/update', apis.update_org_settings, name='update_org_settings'),
    path('<org_id>/delete/<user_id>', apis.remove_user_from_org, name='remove_user_from_org'),
    path('<org_id>/<user_id>/admin/disable', apis.disable_admin_org, name='disable_admin_org'),
    path('<org_id>/<user_id>/admin/enable', apis.enable_admin_org, name='enable_admin_org'),
    path('addorg', apis.create_organization, name='create_organization'),
    path('<organization_id>/adduser', apis.invite_user, name='invite_user'),
    path('<organization_id>/enable', apis.enable_org, name='enable_org'),
    path('<organization_id>/disable', apis.disable_org, name='disable_org'),
    path('<organization_id>/remove', apis.remove_org, name='remove_org'),

    # API Token Management
    path('token/get', apis.get_curruser_authtoken, name='get_curruser_authtoken'),
    path('token/get/<user_id>)', apis.get_user_authtoken, name='get_user_authtoken'),
    path('token/renew', apis.renew_curruser_authtoken, name='renew_curruser_authtoken'),
    path('token/renew/<user_id>', apis.renew_user_authtoken, name='renew_user_authtoken'),
    path('token/delete', apis.delete_curruser_authtoken, name='delete_curruser_authtoken'),
    path('token/delete/<user_id>', apis.delete_user_authtoken, name='delete_user_authtoken'),
]

# url(r'^(?P<organization_pk>[\d]+)/people/add/$',
#     view=login_required(views.OrganizationUserCreate.as_view()),
