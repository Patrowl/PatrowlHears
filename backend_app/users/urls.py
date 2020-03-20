# -*- coding: utf-8 -*-
from django.urls import path
from . import serializers, apis

# Serialized data
urlpatterns = [
    path('api/current', serializers.CurrentUserView.as_view()),
    path('activate/<token>', apis.activate_user, name='activate_user'),
    path('<org_id>/delete/<user_id>', apis.remove_user_from_org, name='remove_user_from_org'),
    path('<organization_pk>/add', apis.CustOrganizationUserCreate.as_view())
]

# url(r'^(?P<organization_pk>[\d]+)/people/add/$',
#     view=login_required(views.OrganizationUserCreate.as_view()),
