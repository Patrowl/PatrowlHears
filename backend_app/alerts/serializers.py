# from django.contrib.auth.models import User
from django_filters import rest_framework as filters
from django_filters import FilterSet, OrderingFilter
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import AlertingRule


class AlertingRuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AlertingRule
        fields = [
            'id', 'title', 'target',
            'action', 'conditions', 'check_fields', 'severity', 'template',
            'on_monitored', 'in_bulk', 'enabled',
            'created_at', 'updated_at'
        ]
