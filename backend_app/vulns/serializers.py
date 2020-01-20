from rest_framework import serializers
from .models import Vuln, ExploitMetadata, ThreatMetadata


class VulnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vuln
        fields = [
            'cve_id', 'summary', 'published', 'modified', 'assigner',
            'cvss', 'cvss_time', 'cvss_vector',
            'cwe', 'access', 'impact',
            'is_exploitable',
            'is_confirmed',
            'is_in_the_news',
            'is_in_the_wild',
            'created_at', 'updated_at']


class ExploitMetadataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExploitMetadata
        fields = [
            'vuln', 'links', 'notes',
            'trust_level', 'tlp_level', 'source',
            'availability', 'type', 'maturity',
            'created_at', 'updated_at']


class ThreatMetadataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ThreatMetadata
        fields = [
            'vuln', 'links', 'notes',
            'trust_level', 'tlp_level', 'source',
            'is_in_the_wild', 'is_in_the_news',
            'created_at', 'updated_at']
