from django.db.models import Q, Count, F
from rest_framework import serializers
from django_filters import FilterSet, OrderingFilter, CharFilter, BooleanFilter, NumberFilter#, AllLookupsFilter
# from rest_framework_filters import FilterSet, OrderingFilter, CharFilter, BooleanFilter, NumberFilter, AllLookupsFilter
from django.utils.translation import gettext_lazy as _
from common.utils.serializers import DynamicFieldsModelSerializer
from .models import (
    Vuln, ExploitMetadata, ThreatMetadata,
    OrgExploitMetadata, OrgThreatMetadata
)
from cpe import CPE as _CPE


class VulnSerializer(DynamicFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
    exploit_count = serializers.SerializerMethodField()
    monitored = serializers.SerializerMethodField()
    cwe_id = serializers.SerializerMethodField()
    cwe_name = serializers.SerializerMethodField()
    cwe_refs = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    def get_exploit_count(self, instance):
        # return instance.exploitmetadata_set.count() + instance.orgexploitmetadata_set.filter(organization_id=instance.org).count()
        return instance.exploitmetadata_set.count()

    def get_monitored(self, instance):
        # print(instance)
        # print(dir(instance))
        if hasattr(instance, 'monitored'):
            return instance.monitored
        else:
            return False

    def get_cwe_id(self, instance):
        if instance.cwe is not None:
            return instance.cwe.cwe_id
        else:
            return ""

    def get_cwe_name(self, instance):
        if instance.cwe is not None:
            return instance.cwe.name
        else:
            return ""

    def get_cwe_refs(self, instance):
        if instance.cwe is not None:
            return instance.cwe.refs
        else:
            return ""

    def get_products(self, instance):
        return [{'id': p.id, 'name': p.name, 'vendor': p.vendor.name} for p in instance.products.all()]

    class Meta:
        model = Vuln
        fields = [
            'id',
            'uuid',
            'cveid',
            'cve_id',
            'summary', 'published', 'modified', 'assigner',
            'cvss', 'cvss_time', 'cvss_vector',
            'cvss3', 'cvss3_vector', 'cvss3_metrics',
            'cwe_id', 'cwe_name', 'cwe_refs',
            'access', 'impact',
            'is_exploitable',
            'exploit_count',
            'score',
            'is_confirmed',
            'is_in_the_news',
            'is_in_the_wild',
            'vulnerable_products',
            'vulnerable_product_versions',
            'products',
            'vulnerable_packages_versions',
            'monitored',
            'reflinks',
            'reflinkids',
            'created_at',
            'updated_at'
        ]
    #
    # def __init__(self, *args, **kwargs):
    #     # Instantiate the superclass normally
    #     super(VulnSerializer, self).__init__(*args, **kwargs)
    #
    #     fields = self.context['request'].query_params.get('fields')
    #     if fields:
    #         fields = fields.split(',')
    #         # Drop any fields that are not specified in the `fields` argument.
    #         allowed = set(fields)
    #         existing = set(self.fields.keys())
    #         for field_name in existing - allowed:
    #             self.fields.pop(field_name)


class ExploitCountOrderingFilter(OrderingFilter):
    def filter(self, qs, value):
        if value is not None and 'exploit_count' in value:
            qs = qs.prefetch_related('exploitmetadata_set', 'orgexploitmetadata_set').annotate(exploit_count=Count('exploitmetadata')+Count('orgexploitmetadata')).order_by('exploit_count')
            value.remove('exploit_count')
        if value is not None and '-exploit_count' in value:
            qs = qs.prefetch_related('exploitmetadata_set', 'orgexploitmetadata_set').annotate(exploit_count=Count('exploitmetadata')+Count('orgexploitmetadata')).order_by('-exploit_count')
            value.remove('-exploit_count')
        return super(ExploitCountOrderingFilter, self).filter(qs, value)


class VulnFilter(FilterSet):
    search = CharFilter(method='filter_search', field_name='search')
    cvss_vector = CharFilter(field_name='cvss_vector')
    cvss3_vector = CharFilter(field_name='cvss3_vector')
    exploit_count__gt = NumberFilter(method='filter_exploit_count__gt', field_name='exploit_count')
    exploit_count__gte = NumberFilter(method='filter_exploit_count__gte', field_name='exploit_count')
    exploit_count__lt = NumberFilter(method='filter_exploit_count__lt', field_name='exploit_count')
    exploit_count__lte = NumberFilter(method='filter_exploit_count__lte', field_name='exploit_count')
    cwe_id = CharFilter(method='filter_cwe_id', field_name='cwe_id')
    cpe = CharFilter(method='filter_cpe', field_name='cpe')
    vendor = CharFilter(method='filter_vendor', field_name='vendor')
    vendor_name = CharFilter(method='filter_vendor_name', field_name='vendor_name')
    product = CharFilter(method='filter_product', field_name='product')
    product_name = CharFilter(method='filter_product_name', field_name='product_name')
    product_version = CharFilter(method='filter_product_version', field_name='product_version')
    package = CharFilter(method='filter_package', field_name='package')
    package_name = CharFilter(method='filter_package_name', field_name='package_name')
    monitored = BooleanFilter(method='filter_monitored', field_name='monitored')
    is_exploitable = BooleanFilter(field_name='is_exploitable')
    is_confirmed = BooleanFilter(field_name='is_confirmed')
    is_in_the_news = BooleanFilter(field_name='is_in_the_news')
    is_in_the_wild = BooleanFilter(field_name='is_in_the_wild')
    access_vector = CharFilter(method='filter_access_vector', field_name='access_vector')
    access_complexity = CharFilter(method='filter_access_complexity', field_name='access_complexity')
    access_authentication = CharFilter(method='filter_access_authentication', field_name='access_authentication')
    impact_integrity = CharFilter(method='filter_impact_integrity', field_name='impact_integrity')
    impact_availability = CharFilter(method='filter_impact_availability', field_name='impact_availability')
    impact_confidentiality = CharFilter(method='filter_impact_confidentiality', field_name='impact_confidentiality')

    def filter_exploit_count__gt(self,  queryset, name, value):
        queryset = queryset.annotate(exploit_count=Count('exploitmetadata')).filter(exploit_count__gte=value)

    def filter_exploit_count__gte(self,  queryset, name, value):
        queryset = queryset.annotate(exploit_count=Count('exploitmetadata'))
        return queryset.filter(exploit_count__gt=value)

    def filter_exploit_count__lt(self,  queryset, name, value):
        queryset = queryset.annotate(exploit_count=Count('exploitmetadata')).filter(exploit_count__lt=value)

    def filter_exploit_count__lte(self,  queryset, name, value):
        return queryset.annotate(exploit_count=Count('exploitmetadata')).filter(exploit_count__lte=value)

    def filter_cwe_id(self,  queryset, name, value):
        return queryset.filter(cwe__cwe_id__icontains=value)

    def filter_cpe(self,  queryset, name, value):
        try:
            c = value.split(':')
            vendor = c[3]
            product = c[4]
            version = c[5]
            f = {
                "products__vendor__name__contains": vendor,
                "products__name__contains": product,
                "vulnerable_product_versions__{}__{}__contains".format(vendor, product): version
            }
            return queryset.prefetch_related('products', 'products__vendor').filter(**f).distinct()
        except Exception:
            pass
        return queryset.filter(vulnerable_products__icontains=value)

    def filter_search(self,  queryset, name, value):
        if type(value) == str:
            value = value.lower()

        # @ todo twist search value (_ -> " ", " " -> _)
        return queryset.prefetch_related('exploitmetadata_set', 'orgexploitmetadata_set', 'products', 'products__vendor').filter(
            Q(cveid__icontains=value) |
            Q(summary__icontains=value) |
            # Q(vulnerable_products__contained_by=[value]) #|
            Q(products__vendor__name__contains=value) |
            Q(products__name__contains=value)
        ).distinct()

    def filter_vendor(self,  queryset, name, value):
        return queryset.filter(products__vendor__in=[value])

    def filter_vendor_name(self,  queryset, name, value):
        if type(value) == str:
            value = value.lower().replace(" ", "_")
        return queryset.filter(products__vendor__name__contains=value)

    def filter_product(self,  queryset, name, value):
        return queryset.filter(products__in=[value])

    def filter_product_name(self,  queryset, name, value):
        if type(value) == str:
            value = value.lower().replace(" ", "_")
        return queryset.filter(products__name__contains=value)

    def filter_product_version(self,  queryset, name, value):
        if type(value) == str:
            value = value.lower()
        # print(value)

        if 'product_name' in self.data.keys() and 'vendor_name' in self.data.keys():
            f = {"vulnerable_product_versions__{}__{}__contains".format(
                self.data['vendor_name'].lower().replace(" ", "_"),
                self.data['product_name'].lower().replace(" ", "_")): value}
            return queryset.prefetch_related('products', 'products__vendor').filter(**f).distinct()

        return queryset.filter(vulnerable_product_versions__all__contains=value).distinct()

    def filter_package(self,  queryset, name, value):
        return queryset.filter(packages__in=[value])

    def filter_package_name(self,  queryset, name, value):
        if type(value) == str:
            value = value.lower().replace(" ", "_")
        return queryset.filter(packages__name__contains=value)

    def filter_monitored(self,  queryset, name, value):
        return queryset.filter(monitored=value)

    # Access
    def filter_access_vector(self,  queryset, name, value):
        return queryset.filter(access__vector=value)

    def filter_access_complexity(self,  queryset, name, value):
        return queryset.filter(access__complexity=value)

    def filter_access_authentication(self,  queryset, name, value):
        return queryset.filter(access__authentication=value)

    # Impact
    def filter_impact_integrity(self,  queryset, name, value):
        return queryset.filter(impact__integrity=value)

    def filter_impact_availability(self,  queryset, name, value):
        return queryset.filter(impact__availability=value)

    def filter_impact_confidentiality(self,  queryset, name, value):
        return queryset.filter(impact__confidentiality=value)


    # sorted_by = OrderingFilter(
    sorted_by = ExploitCountOrderingFilter(
        choices=(
            ('id', _('PHID')), ('-id', _('PHID (Desc)')),
            ('cveid', _('CVE')), ('-cveid', _('CVE (Desc)')),
            ('cvss', _('CVSSv2')), ('-cvss', _('CVSSv2 (Desc)')),
            ('cvss3', _('CVSSv3')), ('-cvss3', _('CVSSv3 (Desc)')),
            ('score', _('Score')), ('-score', _('Score (Desc)')),
            ('exploit_count', _('NB Exploits')), ('-exploit_count', _('NB Exploits (Desc)')),
            ('summary', _('Summary')), ('-summary', _('Summary (Desc)')),
            ('monitored', _('Monitored')), ('-monitored', _('Monitored (Desc)')),
            ('published', _('Published')), ('-published', _('Published (Desc)')),
            ('updated_at', _('Updated at')), ('-updated_at', _('Updated_at (Desc)')),
            ('is_exploitable', _('Exploitable')), ('-is_exploitable', _('Exploitable (Desc)')),
            ('is_in_the_news', _('Is in the News')), ('-is_in_the_news', _('Is in the News (Desc)')),
            ('is_confirmed', _('Confirmed')), ('-is_confirmed', _('Not confirmed')),
        )
    )

    class Meta:
        model = Vuln
        fields = {
            'summary': ['exact', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith', 'iendswith'],
            # 'search': ['exact', 'contains', 'icontains'],
            'score': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'updated_at': ['exact', 'gt', 'gte', 'lt', 'lte'],
            # 'monitored': ['exact'],
            'cveid': ['exact', 'contains', 'icontains'],
            'cvss': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'cvss_vector': ['exact', 'contains', 'icontains'],
            'cvss3': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'cvss3_vector': ['exact', 'contains', 'icontains'],
            # 'exploit_count__gt': '__all__',
            # 'exploit_count__gte': '__all__',
            # 'exploit_count__lt': '__all__',
            # 'exploit_count__lte': '__all__',
        }


class ExploitMetadataSerializer(serializers.HyperlinkedModelSerializer):
    vp = serializers.SerializerMethodField()
    relevancy_level = serializers.SerializerMethodField()
    cveid = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    scope = serializers.SerializerMethodField()

    def get_vp(self, instance):
        if hasattr(instance, 'vp'):
            return instance.vp
        else:
            return []

    def get_relevancy_level(self, instance):
        return instance.get_relevancy_level()

    def get_cveid(self, instance):
        return instance.vuln.cveid

    def get_products(self, instance):
        return [{'id': p.id, 'name': p.name, 'vendor': p.vendor.name} for p in instance.vuln.products.all()]

    def get_scope(self, instance):
        return 'public'

    class Meta:
        model = ExploitMetadata
        fields = [
            'id',
            'uuid',
            'publicid',
            'vuln_id',
            'vp',
            'link',
            'notes',
            'trust_level', 'tlp_level', 'source',
            'availability', 'type', 'maturity',
            # 'raw',
            'published', 'modified',
            'relevancy_level',
            'created_at', 'updated_at',
            'cveid', 'products', 'scope'
        ]


class ExploitMetadataFilter(FilterSet):
    search = CharFilter(method='filter_search', field_name='search')
    cveid = CharFilter(method='filter_cveid', field_name='cveid')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(link__icontains=value) |
            Q(notes__icontains=value) |
            Q(vuln__cveid__icontains=value)
        )

    def filter_cveid(self,  queryset, name, value):
        return queryset.filter(vuln__cveid=value)

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('trust_level', _('Trust Level')),
            ('-trust_level', _('Trust Level (Desc)')),
            ('tlp_level', _('TLP Level')),
            ('-tlp_level', _('TLP Level (Desc)')),
            ('availability', _('Availability')),
            ('-availability', _('Availability (Desc)')),
            ('link', _('Link')),
            ('-link', _('Link (Desc)')),
            ('updated_at', _('Updated at')),
            ('-updated_at', _('Updated_at (Desc)')),
        )
    )

    class Meta:
        model = ExploitMetadata
        fields = {
            'link': ['icontains'],
            'notes': ['icontains'],
            # 'cveid': ['exact', 'contains', 'icontains'],
        }


class OrgExploitMetadataSerializer(ExploitMetadataSerializer):

    def get_scope(self, instance):
        return 'private'

    class Meta:
        model = OrgExploitMetadata
        fields = [
            'id', 'uuid', 'publicid',
            'vuln_id', 'cveid',
            'vp',
            'link',
            'notes',
            'trust_level', 'tlp_level', 'source',
            'availability', 'type', 'maturity',
            'relevancy_level',
            'published', 'modified',
            'created_at', 'updated_at', 'scope'
        ]


class OrgExploitMetadataFilter(ExploitMetadataFilter):

    sorted_by = OrderingFilter(
        choices=(
            ('trust_level', _('Trust Level')),
            ('-trust_level', _('Trust Level (Desc)')),
            ('tlp_level', _('TLP Level')),
            ('-tlp_level', _('TLP Level (Desc)')),
            ('availability', _('Availability')),
            ('-availability', _('Availability (Desc)')),
            ('link', _('Link')),
            ('-link', _('Link (Desc)')),
            ('updated_at', _('Updated at')),
            ('-updated_at', _('Updated_at (Desc)')),
        )
    )

    class Meta:
        model = OrgExploitMetadata
        fields = {
            'link': ['icontains'],
            'notes': ['icontains'],
            # 'cveid': ['exact', 'contains', 'icontains'],
        }


class ThreatMetadataSerializer(serializers.HyperlinkedModelSerializer):
    scope = serializers.SerializerMethodField()
    cveid = serializers.SerializerMethodField()

    def get_scope(self, instance):
        return 'public'

    def get_cveid(self, instance):
        return instance.vuln.cveid

    class Meta:
        model = ThreatMetadata
        fields = [
            'id', 'uuid', 'vuln_id', 'cveid',
            'link', 'notes',
            'trust_level', 'tlp_level', 'source',
            'is_in_the_wild', 'is_in_the_news',
            'raw', 'published', 'modified',
            'created_at', 'updated_at',
            'scope'
        ]


class ThreatMetadataFilter(FilterSet):
    search = CharFilter(method='filter_search', field_name='search')
    cveid = CharFilter(method='filter_cveid', field_name='cveid')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(link__icontains=value) |
            Q(notes__icontains=value) |
            Q(vuln__cveid__icontains=value)
        )

    def filter_cveid(self,  queryset, name, value):
        return queryset.filter(vuln__cveid=value)

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('trust_level', _('Trust Level')),
            ('-trust_level', _('Trust Level (Desc)')),
            ('tlp_level', _('TLP Level')),
            ('-tlp_level', _('TLP Level (Desc)')),
            ('availability', _('Availability')),
            ('-availability', _('Availability (Desc)')),
            ('link', _('Link')),
            ('-link', _('Link (Desc)')),
            ('updated_at', _('Updated at')),
            ('-updated_at', _('Updated_at (Desc)')),
        )
    )

    class Meta:
        model = ThreatMetadata
        fields = {
            'link': ['icontains'],
            'notes': ['icontains'],
            # 'cveid': ['exact', 'contains', 'icontains'],
        }


class OrgThreatMetadataSerializer(ThreatMetadataSerializer):

    def get_scope(self, instance):
        return 'private'

    class Meta:
        model = OrgThreatMetadata
        fields = [
            'id', 'uuid', 'vuln_id', 'cveid',
            'link', 'notes',
            'trust_level', 'tlp_level', 'source',
            'is_in_the_wild', 'is_in_the_news',
            'raw', 'published', 'modified',
            'created_at', 'updated_at',
            'scope'
        ]


class OrgThreatMetadataFilter(ThreatMetadataFilter):

    sorted_by = OrderingFilter(
        choices=(
            ('trust_level', _('Trust Level')),
            ('-trust_level', _('Trust Level (Desc)')),
            ('tlp_level', _('TLP Level')),
            ('-tlp_level', _('TLP Level (Desc)')),
            ('availability', _('Availability')),
            ('-availability', _('Availability (Desc)')),
            ('link', _('Link')),
            ('-link', _('Link (Desc)')),
            ('updated_at', _('Updated at')),
            ('-updated_at', _('Updated_at (Desc)')),
        )
    )

    class Meta:
        model = OrgThreatMetadata
        fields = {
            'link': ['icontains'],
            'notes': ['icontains'],
            # 'cveid': ['exact', 'contains', 'icontains'],
        }
