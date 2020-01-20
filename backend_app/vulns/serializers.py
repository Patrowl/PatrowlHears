from rest_framework import serializers
from .models import Vuln, ExploitMetadata, ThreatMetadata


class VulnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vuln
        fields = [
            'id',
            'cve_id', 'summary', 'published', 'modified', 'assigner',
            'cvss', 'cvss_time', 'cvss_vector',
            'cwe_id', 'access', 'impact',
            'is_exploitable',
            'is_confirmed',
            'is_in_the_news',
            'is_in_the_wild',
            # 'exploitmetadata_set',
            # 'threatmetadata_set',
            'created_at', 'updated_at']


class ExploitMetadataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExploitMetadata
        fields = [
            'id', 'publicid',
            'vuln', 'link', 'notes',
            'trust_level', 'tlp_level', 'source',
            'availability', 'type', 'maturity',
            'raw', 'published', 'modified',
            'created_at', 'updated_at']


class ThreatMetadataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ThreatMetadata
        fields = [
            'id',
            'vuln', 'link', 'notes',
            'trust_level', 'tlp_level', 'source',
            'is_in_the_wild', 'is_in_the_news',
            'raw', 'published', 'modified',
            'created_at', 'updated_at']
