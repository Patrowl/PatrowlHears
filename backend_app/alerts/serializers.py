from rest_framework import serializers
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
