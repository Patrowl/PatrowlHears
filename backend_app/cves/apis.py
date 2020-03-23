from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import Case, BooleanField, When
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from organizations.models import OrganizationUser, Organization
from common.utils import cvesearch, organization
from common.utils.pagination import StandardResultsSetPagination
from .models import CVE, CPE, CWE, Bulletin, Vendor, Product
from .serializers import (
    CVESerializer, CPESerializer, CWESerializer, BulletinSerializer,
    VendorSerializer, ProductSerializer, ProductDetailSerializer,
    CVEFilter, CPEFilter, VendorFilter, ProductFilter, ProductDetailFilter,
    BulletinFilter
)
from .tasks import (
    sync_cwes_task, sync_cpes_task, sync_cves_task, sync_vias_task,
    sync_bulletins_task
)


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
    queryset = CPE.objects.all().order_by('id').distinct()
    serializer_class = CPESerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ('vendor', 'product', 'monitored',)
    filterset_class = CPEFilter
    pagination_class = StandardResultsSetPagination


class VendorSet(viewsets.ModelViewSet):
    """API endpoint that allows Vendors to be viewed or edited."""

    # queryset = CPE.objects.all().values('vendor').order_by('vendor').distinct()
    queryset = Vendor.objects.all().order_by('-name').distinct()
    serializer_class = VendorSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ('vendor',)
    filterset_fields = ('name',)
    filterset_class = VendorFilter
    pagination_class = StandardResultsSetPagination


class ProductSet(viewsets.ModelViewSet):
    """API endpoint that allows Products to be viewed or edited."""

    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ('product', 'title', 'vector',)
    filterset_fields = ('name')
    filterset_class = ProductFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        current_user = self.request.user
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=current_user, org_id=org_id)
        monitored_products = org.org_monitoring_list.products.all()
        return Product.objects.all().prefetch_related(
            'vendor', 'org_monitoring_list__products', 'org_monitoring_list'
            ).annotate(
                monitored=Case(
                    When(id__in=monitored_products, then=True),
                    default=False,
                    output_field=BooleanField()
                )
            ).order_by('-name').distinct()


class ProductDetailSet(viewsets.ModelViewSet):
    """API endpoint that allows ProductDetails to be viewed or edited."""

    serializer_class = ProductDetailSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ('product', 'title', 'vector',)
    filterset_fields = ('name')
    filterset_class = ProductDetailFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        current_user = self.request.user
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=current_user, org_id=org_id)

        monitored_products = org.org_monitoring_list.products.all()
        return Product.objects.all().prefetch_related(
            'vendor', 'org_monitoring_list__products', 'org_monitoring_list', 'productversion_set'
            ).annotate(
                monitored=Case(
                    When(id__in=monitored_products, then=True),
                    default=False,
                    output_field=BooleanField()
                )
            ).order_by('-name').distinct()


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
@permission_classes([IsAdminUser])
def sync_cwes(self):
    cvesearch.sync_cwes_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_cwes_async(self):
    sync_cwes_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_cpes(self):
    cvesearch.sync_cpes_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_cpes_async(self):
    sync_cpes_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_cves(self):
    cvesearch.sync_cves_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_cve(self, cve_id):
    cvesearch.sync_cve_fromdb(cve_id)
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_cve_info(self, cve_id):
    cve = get_object_or_404(CVE, cve_id=cve_id)
    return JsonResponse(model_to_dict(cve), safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_cves_async(self):
    sync_cves_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_vias(self):
    cvesearch.sync_via_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_vias_async(self):
    sync_vias_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_bulletins(self):
    cvesearch.sync_bulletins_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_bulletins_async(self):
    sync_bulletins_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)

#
# @api_view(['GET'])
# def sync_exploits(self):
#     cvesearch.sync_exploits_fromvia()
#     return JsonResponse("done.", safe=False)


@api_view(['GET'])
def get_product_vulnerabilities(self, product_id):
    from vulns.models import Vuln
    product = get_object_or_404(Product, id=product_id)
    p = ":{}:{}:".format(product.vendor.name, product.name)
    res = []
    for vuln in Vuln.objects.all().only('id', 'vulnerable_products'):
        # is_related = False
        # for vvp in vuln.vulnerable_products:
        #     if p in vvp:
        #         res.append(vuln.to_dict())
        #         is_related = True
        #         break
        #     if is_related:
        #         break
        if p in vuln.vulnerable_products:
            res.append(vuln.to_dict())

    return JsonResponse(res, safe=False)
