from django.db.models import Q
from django_filters import FilterSet, OrderingFilter, CharFilter, BooleanFilter, NumberFilter
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import CVE, CPE, CWE, Bulletin, Vendor, Product, Package


class CVESerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CVE
        fields = [
            'id',
            'cve_id', 'summary', 'assigner',
            'published', 'modified',
            'cvss', 'cvss_time', 'cvss_vector',
            'cwe_id', 'access', 'impact', 'vulnerable_products',
            'references', 'bulletins',
            'monitored',
            'created_at', 'updated_at',
        ]


class CVEFilter(FilterSet):
    search = CharFilter(method='filter_search')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(cve_id__icontains=value) |
            Q(summary__icontains=value)
        )

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('cve_id', _('CVE-ID')),
            ('-cve_id', _('CVE-ID (desc)')),
            ('cvss', _('CVSSv2')),
            ('-cvss', _('CVSSv2 (desc)')),
            ('summary', _('Summary')),
            ('-summary', _('Summary (desc)')),
            ('modified', _('Modified')),
            ('-modified', _('Modified (desc)')),
            ('monitored', _('Monitored')),
            ('-monitored', _('Monitored (desc)')),
        )
    )

    class Meta:
        model = CVE
        fields = {
            'cve_id': ['icontains', 'exact'],
            'cvss': ['icontains'],
            'summary': ['icontains'],
            'search': ['icontains'],
        }


class CPESerializer(serializers.HyperlinkedModelSerializer):
    # monitored = serializers.SerializerMethodField()
    #
    # def get_monitored(self, instance):
    #     return instance.is_monitored()

    class Meta:
        model = CPE
        fields = [
            'id', 'title', 'vector',
            'vendor',
            'product',
            'vulnerable_products',
            # 'monitored',
            'updated_at'
        ]


class CPEFilter(FilterSet):
    sorted_by = OrderingFilter(
        choices=(
            # ('vendor', _('Vendor')),
            # ('-vendor', _('Vendor (Desc)')),
            # ('product', _('Product')),
            # ('-product', _('Product (Desc)')),
            ('title', _('Title')),
            ('-title', _('Title (Desc)')),
            ('vector', _('Vector')),
            ('-vector', _('Vector (desc)')),
            # ('monitored', _('Monitored')),
            # ('-monitored', _('Monitored (desc)')),
        )
    )

    class Meta:
        model = CPE
        fields = {
            # 'vendor': ['icontains', 'exact'],
            # 'product': ['icontains', 'exact'],
            'title': ['icontains', 'exact'],
            'vector': ['icontains', 'exact'],
            # 'monitored': [''],
        }


class VendorSerializer(serializers.HyperlinkedModelSerializer):
    monitored = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    def get_monitored(self, instance):
        return instance.monitored

    def get_products_count(self, instance):
        return instance.products_count

    class Meta:
        model = Vendor
        fields = ['name', 'id', 'monitored', 'products_count']


class VendorFilter(FilterSet):
    search = CharFilter(method='filter_search')
    monitored = BooleanFilter(method='filter_monitored')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )

    def filter_monitored(self,  queryset, name, value):
        return queryset.filter(monitored=value)

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('name', _('Name')),
            ('-name', _('Name (Desc)')),
            ('monitored', _('Monitored')),
            ('-monitored', _('Monitored (desc)')),
            ('updated_at', _('Updated at')),
            ('-updated_at', _('Updated at (desc)')),
        )
    )

    class Meta:
        model = Vendor
        fields = {
            'name': ['icontains']
        }


class ProductFilter(FilterSet):
    search = CharFilter(method='filter_search')
    vendor = CharFilter(method='filter_vendor')
    vendor_id = CharFilter(method='filter_vendor_id')
    monitored = BooleanFilter(method='filter_monitored')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(vendor__name__icontains=value) |
            Q(name__icontains=value)
        )

    def filter_vendor(self,  queryset, name, value):
        return queryset.filter(vendor__name=value)

    def filter_vendor_id(self,  queryset, name, value):
        return queryset.filter(vendor=value)

    def filter_monitored(self,  queryset, name, value):
        return queryset.filter(monitored=value)

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('vendor__name', _('Vendor Name')),
            ('-vendor__name', _('Vendor Name (Desc)')),
            ('vendor', _('Vendor')),
            ('-vendor', _('Vendor (Desc)')),
            ('name', _('Product Name')),
            ('-name', _('Product Name (Desc)')),
            ('monitored', _('Monitored')),
            ('-monitored', _('Monitored (desc)')),
            ('updated_at', _('Updated at')),
            ('-updated_at', _('Updated at (desc)')),
        )
    )

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'vendor__name': ['icontains'],
            'monitored': ['exact'],
        }


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    vendor = serializers.SerializerMethodField()
    monitored = serializers.SerializerMethodField()
    # vulns_count = serializers.SerializerMethodField()

    def get_vendor(self, instance):
        return instance.vendor.name

    def get_monitored(self, instance):
        return instance.monitored

    # def get_vulns_count(self, instance):
    #     return instance.vulns_count

    class Meta:
        model = Product
        fields = ['id', 'name', 'vendor', 'monitored']
        # fields = ['id', 'name', 'vendor', 'monitored', 'vulns_count']


class ProductDetailFilter(FilterSet):
    search = CharFilter(method='filter_search')
    monitored = BooleanFilter(method='filter_monitored')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(vendor__name__icontains=value) |
            Q(name__icontains=value)
        )

    def filter_monitored(self,  queryset, name, value):
        return queryset.filter(monitored=value)

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('vendor__name', _('Vendor')),
            ('-vendor__name', _('Vendor (Desc)')),
            ('name', _('Product Name')),
            ('-name', _('Product Name (Desc)')),
            ('monitored', _('Monitored')),
            ('-monitored', _('Monitored (desc)')),
        )
    )

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'vendor__name': ['icontains'],
            'monitored': ['exact'],
        }


class ProductDetailSerializer(serializers.HyperlinkedModelSerializer):
    vendor = serializers.SerializerMethodField()
    vendor_id = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()
    monitored = serializers.SerializerMethodField()

    def get_vendor(self, instance):
        return instance.vendor.name

    def get_vendor_id(self, instance):
        return instance.vendor.id

    def get_versions(self, instance):
        versions = []
        for v in instance.productversion_set.all().order_by('-version').distinct('version'):
            versions.append(v.to_dict())
        return versions

    def get_monitored(self, instance):
        return instance.monitored

    class Meta:
        model = Product
        fields = ['id', 'name', 'vendor', 'vendor_id', 'monitored', 'versions', 'monitored']


class CWESerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CWE
        fields = [
            'id', 'cwe_id', 'name', 'description', 'refs'
        ]


class BulletinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bulletin
        fields = [
            'id',
            'publicid', 'vendor', 'title',
            'severity', 'impact', 'published',
            'monitored'
        ]


class BulletinFilter(FilterSet):
    search = CharFilter(method='filter_search')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(publicid__icontains=value) |
            Q(vendor__icontains=value) |
            Q(title__icontains=value)
        )

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('publicid', _('Public ID')),
            ('-publicid', _('Public ID (desc)')),
            ('vendor', _('Vendor')),
            ('-vendor', _('Vendor (desc)')),
            ('title', _('Title')),
            ('-title', _('Title (desc)')),
            ('severity', _('Severity')),
            ('-severity', _('Severity (desc)')),
            ('published', _('Published')),
            ('-published', _('Published (desc)')),
            ('monitored', _('Monitored')),
            ('-monitored', _('Monitored (desc)')),
        )
    )


class PackageSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.SerializerMethodField()
    vulns = serializers.SerializerMethodField()
    vulns_cnt = serializers.SerializerMethodField()
    monitored = serializers.SerializerMethodField()

    def get_type(self, instance):
        return instance.type.name

    def get_vulns_cnt(self, instance):
        return instance.vulns.all().count()

    def get_vulns(self, instance):
        vulns = []
        # print(instance.vulns.all())

        for v in instance.vulns.all():
            vulns.append({
                'id': v.id,
                'summary': v.summary,
                'cveid': v.cveid,
                'score': v.score,
                'cvss': v.cvss,
                'cvss_vector': v.cvss_vector,
                'cvss3': v.cvss3,
                'cvss3_vector': v.cvss3_vector,
                'is_exploitable': v.is_exploitable,
                'vulnerable_packages_versions': v.vulnerable_packages_versions,
            })

        return vulns

    def get_monitored(self, instance):
        return instance.monitored

    class Meta:
        model = Package
        fields = ['id', 'name', 'type', 'vulns', 'vulns_cnt', 'monitored']


class PackageFilter(FilterSet):
    type = CharFilter(method='filter_type')
    monitored = BooleanFilter(method='filter_monitored')

    def filter_type(self,  queryset, name, value):
        return queryset.filter(type__name=value)

    def filter_monitored(self,  queryset, name, value):
        return queryset.filter(monitored=value)

    sorted_by = OrderingFilter(
        choices=(
            ('name', _('Package Name')),
            ('-name', _('Package Name (Desc)')),
            ('type', _('Package Type')),
            ('-type', _('Package Type (Desc)')),
            ('monitored', _('Monitored')),
            ('-monitored', _('Monitored (desc)')),
        )
    )

    class Meta:
        model = Package
        fields = {
            'name': ['icontains', 'exact'],
            'monitored': ['exact'],
        }
