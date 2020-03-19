# -*- coding: utf-8 -*-
from django.urls import path
from . import serializers, apis

# Serialized data
urlpatterns = [
    path('api/current', serializers.CurrentUserView.as_view()),
    path('activate/<token>', apis.activate_user, name='activate_user'),
]
