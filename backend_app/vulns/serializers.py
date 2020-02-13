from django.db.models import Q
from rest_framework import serializers
from django_filters import FilterSet, OrderingFilter, CharFilter
from django.utils.translation import gettext_lazy as _
from .models import Vuln, ExploitMetadata, ThreatMetadata
from vpratings.utils import _calc_vprating


class VulnSerializer(serializers.HyperlinkedModelSerializer):
    cve = serializers.SerializerMethodField()
    exploit_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    # vulnerable_products = serializers.SerializerMethodField()

    def get_cve(self, instance):
        return instance.cve_id.cve_id

    def get_exploit_count(self, instance):
        return instance.exploitmetadata_set.count()

    def get_rating(self, instance):
        return _calc_vprating(instance).score

    # def get_vulnerable_products(self, instance):
    #     return instance.cve_id.vulnerable_products

    class Meta:
        model = Vuln
        fields = [
            'id',
            'cve_id_id', 'cve', 'summary', 'published', 'modified', 'assigner',
            'cvss', 'cvss_time', 'cvss_vector',
            'cwe_id', 'access', 'impact',
            'is_exploitable',
            'exploit_count',
            'rating',
            'is_confirmed',
            'is_in_the_news',
            'is_in_the_wild',
            # 'exploitmetadata_set',
            # 'threatmetadata_set',
            'vulnerable_products',
            'monitored',
            'reflinks',
            'reflinkids',
            'created_at', 'updated_at']


class VulnFilter(FilterSet):
    search = CharFilter(method='filter_search', field_name='search')
    # rating = CharFilter(method='filter_rating', field_name='rating')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(cve_id__cve_id__icontains=value) |
            Q(summary__icontains=value)
        )
    #
    # def filter_rating(self,  queryset, name, value):
    #     print(_calc_vprating(self).score)
    #     return queryset.all()

    sorted_by = OrderingFilter(
        choices=(
            ('id', _('PHID')), ('-id', _('PHID (Desc)')),
            ('cve', _('CVE')), ('-cve', _('CVE (Desc)')),
            ('cvss', _('CVSS')), ('-cvss', _('CVSS (Desc)')),
            # ('rating', _('Rating')), ('-rating', _('Rating (Desc)')),
            ('monitored', _('Monitored')), ('-monitored', _('Monitored (Desc)')),
            ('published', _('Published')), ('-published', _('Published (Desc)')),
            ('updated_at', _('Updated at')), ('-updated_at', _('Updated_at (Desc)')),
            ('is_exploitable', _('Exploitable')), ('-is_exploitable', _('Not exploitable')),
            ('is_confirmed', _('Confirmed')), ('-is_confirmed', _('Not confirmed')),
        )
    )

    class Meta:
        model = Vuln
        fields = {
            'summary': ['icontains'],
            'search': ['icontains'],
            # 'rating': [''],
        }


class ExploitMetadataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExploitMetadata
        fields = [
            'id',
            'publicid',
            'vuln_id',
            'link',
            'notes',
            'trust_level', 'tlp_level', 'source',
            'availability', 'type', 'maturity',
            # 'raw',
            'published', 'modified',
            'created_at', 'updated_at'
        ]


class ExploitMetadataFilter(FilterSet):
    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('trust_level', _('Trust Level')), ('-trust_level', _('Trust Level (Desc)')),
            ('tlp_level', _('TLP Level')), ('-tlp_level', _('TLP Level (Desc)')),
            ('availability', _('Availability')), ('-availability', _('Availability (Desc)')),
            ('updated_at', _('Updated at')), ('-updated_at', _('Updated_at (Desc)')),
        )
    )

    class Meta:
        model = ExploitMetadata
        fields = {
            'link': ['icontains'],
            'notes': ['icontains'],
            'vuln_id': ['exact'],
        }


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
