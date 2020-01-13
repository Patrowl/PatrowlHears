# from django.contrib.auth.models import User
from rest_framework import serializers
from .models import MonitoredAsset


class MonitoredAssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonitoredAsset
        fields = ['name', 'type', 'status', 'created_at', 'updated_at']
