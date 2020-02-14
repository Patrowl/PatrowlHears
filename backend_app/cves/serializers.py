# from django.contrib.auth.models import User
# from django_filters import rest_framework as filters
from django.db.models import Q
from django_filters import FilterSet, OrderingFilter, CharFilter
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import CVE, CPE, CWE, Bulletin


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
            'vendor', 'product', 'vulnerable_products',
            'monitored',
            'updated_at'
        ]


class CPEFilter(FilterSet):
    sorted_by = OrderingFilter(
        choices=(
            ('vendor', _('Vendor')),
            ('-vendor', _('Vendor (Desc)')),
            ('product', _('Product')),
            ('-product', _('Product (Desc)')),
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
            'vendor': ['icontains', 'exact'],
            'product': ['icontains', 'exact'],
            'title': ['icontains', 'exact'],
            # 'monitored': [''],
        }


class VendorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CPE
        # fields = ['vendor', 'id', 'monitored']
        fields = ['vendor', 'id']


class VendorFilter(FilterSet):
    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('vendor', _('Vendor')),
            ('-vendor', _('Vendor (Desc)')),
            # ('monitored', _('Monitored')),
            # ('-monitored', _('Monitored (desc)')),
        )
    )

    class Meta:
        model = CPE
        fields = {
            'vendor': ['icontains']
        }


class ProductFilter(FilterSet):
    search = CharFilter(method='filter_search')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(vendor__icontains=value) |
            Q(product__icontains=value)
        )

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('vendor', _('Vendor')),
            ('-vendor', _('Vendor (Desc)')),
            ('product', _('Product')),
            ('-product', _('Product (Desc)')),
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
            'vendor': ['icontains'],
            'product': ['icontains'],
            'title': ['icontains'],
        }


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    monitored = serializers.SerializerMethodField()

    def get_monitored(self, instance):
        return instance.monitored   # Set by ProductSet.get_queryset annotation

    class Meta:
        model = CPE
        fields = ['vendor', 'product', 'monitored']


class CWESerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CWE
        fields = [
            'cwe_id', 'name', 'description'
        ]


class BulletinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bulletin
        fields = [
            'id',
            'publicid', 'vendor', 'title', 'severity', 'impact', 'published',
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
