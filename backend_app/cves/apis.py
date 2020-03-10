from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import Case, When, BooleanField, Value, Subquery
from django_filters import rest_framework as filters
# from rest_framework import filters as drfilters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from common.utils import cvesearch
from common.utils.pagination import StandardResultsSetPagination
from .models import CVE, CPE, CWE, Bulletin
from .serializers import (
    CVESerializer, CPESerializer, CWESerializer, BulletinSerializer,
    VendorSerializer, ProductSerializer,
    CVEFilter, CPEFilter, VendorFilter, ProductFilter, BulletinFilter
)
from .tasks import (
    sync_cwes_task, sync_cpes_task, sync_cves_task, sync_vias_task,
    sync_bulletins_task
)
from monitored_assets.models import MonitoredProduct


class CVESet(viewsets.ModelViewSet):
    """API endpoint that allows CVE to be viewed or edited."""

    queryset = CVE.objects.all().prefetch_related('bulletins').order_by('cve_id')
    serializer_class = CVESerializer
    filterset_class = CVEFilter
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('cve_id', 'cvss', 'summary')
    pagination_class = StandardResultsSetPagination


class CPESet(viewsets.ModelViewSet):
    """API endpoint that allows CPE to be viewed or edited."""

    # queryset = CPE.objects.all().order_by('id').distinct()
    serializer_class = CPESerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('vendor', 'product', 'monitored',)
    filterset_class = CPEFilter
    pagination_class = StandardResultsSetPagination

    queryset = CPE.objects.filter(vendor='apache').order_by('id').distinct()


class VendorSet(viewsets.ModelViewSet):
    """API endpoint that allows Vendors to be viewed or edited."""

    queryset = CPE.objects.all().values('vendor').order_by('vendor').distinct()
    serializer_class = VendorSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('vendor',)
    filterset_class = VendorFilter
    pagination_class = StandardResultsSetPagination


class ProductSet(viewsets.ModelViewSet):
    """API endpoint that allows Products to be viewed or edited."""

    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('product', 'title', 'vector',)
    filterset_class = ProductFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        mp = MonitoredProduct.objects.filter(monitored=True).values('product').distinct()

        if 'vendor_name' in self.kwargs.keys():
            vendor_name = self.kwargs['vendor_name']
            return CPE.objects.filter(vendor=vendor_name).values('title', 'product', 'vector').order_by('title').distinct()
        if 'monitored' in self.request.GET.keys() and self.request.GET.get('monitored') == 'yes':
            # return CPE.objects.filter(product__in=mp).only('vendor', 'product').distinct('vendor', 'product').order_by('vendor', 'product')
            return CPE.objects.filter(product__in=mp).annotate(
                monitored=Value(True, output_field=BooleanField())
            ).distinct('vendor', 'product').order_by('vendor', 'product')

        # return CPE.objects.annotate(
        #     monitored=Case(
        #         When(product__in=Subquery(mp), then=True), default=False, output_field=BooleanField()
        #     )
        # ).distinct('vendor', 'product').order_by('vendor', 'product')
        return CPE.objects.annotate(
            monitored=Case(When(product__in=mp, then=True), default=False, output_field=BooleanField())
        ).distinct('vendor', 'product').order_by('vendor', 'product')


class CWESet(viewsets.ModelViewSet):
    """API endpoint that allows CWE to be viewed or edited."""

    queryset = CWE.objects.all().order_by('cwe_id')
    serializer_class = CWESerializer
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination


class BulletinSet(viewsets.ModelViewSet):
    """API endpoint that allows Bulletin to be viewed or edited."""

    queryset = Bulletin.objects.all().order_by('id')
    serializer_class = BulletinSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BulletinFilter
    pagination_class = StandardResultsSetPagination


@api_view(['GET'])
def sync_cwes(self):
    cvesearch.sync_cwes_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_cwes_async(self):
    sync_cwes_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
def sync_cpes(self):
    cvesearch.sync_cpes_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_cpes_async(self):
    sync_cpes_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
def sync_cves(self):
    cvesearch.sync_cves_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_cve(self, cve_id):
    cvesearch.sync_cve_fromdb(cve_id)
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def get_cve_info(self, cve_id):
    cve = get_object_or_404(CVE, cve_id=cve_id)
    return JsonResponse(model_to_dict(cve), safe=False)


@api_view(['GET'])
def sync_cves_async(self):
    sync_cves_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
def sync_vias(self):
    cvesearch.sync_via_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_vias_async(self):
    sync_vias_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
def sync_bulletins(self):
    cvesearch.sync_bulletins_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_bulletins_async(self):
    sync_bulletins_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)

#
# @api_view(['GET'])
# def sync_exploits(self):
#     cvesearch.sync_exploits_fromvia()
#     return JsonResponse("done.", safe=False)


@api_view(['GET'])
def get_vendors(self):
    filter = self.GET.get('name', None)
    res = []
    if filter is not None:
        res = CPE.objects.filter(vendor__icontains=filter).values('title').order_by('title').distinct()
    else:
        res = CPE.objects.all().values('title').order_by('title').distinct()
    return JsonResponse(list(res), safe=False)


@api_view(['GET'])
def get_products(self, vendor):
    filter = self.GET.get('name', None)
    res = []
    if filter is not None:
        res = CPE.objects.filter(vendor=vendor, product__icontains=filter).values_list('product', flat=True).order_by('product').distinct()
    else:
        res = CPE.objects.filter(vendor=vendor).values_list('product', flat=True).order_by('product').distinct()
    return JsonResponse(list(res), safe=False)
