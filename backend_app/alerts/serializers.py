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
            'cve_id', 'summary', 'assigner',
            'published', 'modified',
            'cvss', 'cvss_time', 'cvss_vector',
            'cwe_id', 'access', 'impact', 'vulnerable_products',
            'references', 'bulletins',
            'created_at', 'updated_at'
        ]
