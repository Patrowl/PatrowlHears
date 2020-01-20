from rest_framework import serializers
from .models import VPRating


class VPRatingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VPRating
        fields = ['vector', 'vuln', 'score', 'data', 'created_at', 'updated_at']
