# -*- coding: utf-8 -*-
from django.urls import path
from . import serializers

# Serialized data
urlpatterns = [
    path('api/current', serializers.CurrentUserView.as_view()),
]
