from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import Case, BooleanField, When, Count
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from common.utils import cvesearch, organization, get_api_default_permissions
from common.utils.pagination import StandardResultsSetPagination
from .models import CVE, CPE, CWE, Bulletin, Vendor, Product, Package
from .serializers import (
    CVESerializer, CPESerializer, CWESerializer, BulletinSerializer,
    VendorSerializer, ProductSerializer, ProductDetailSerializer,
    CVEFilter, CPEFilter, VendorFilter, ProductFilter, ProductDetailFilter,
    BulletinFilter,
    PackageSerializer, PackageFilter
)
from .tasks import (
    sync_cwes_task, sync_cpes_task, sync_cves_task, sync_cves_fromyear_task, sync_cves_atyear_task,
    sync_vias_task, sync_bulletins_task, sync_cve_task
)


class CVESet(viewsets.ModelViewSet):
    """API endpoint that allows CVE to be viewed or edited."""

    queryset = CVE.objects.all().prefetch_related('bulletins').order_by('cve_id')
    serializer_class = CVESerializer
    filterset_class = CVEFilter
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('cve_id', 'cvss', 'summary')
    pagination_class = StandardResultsSetPagination
    #
    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]

    def get_permissions(self):
        return get_api_default_permissions(self)


class CPESet(viewsets.ModelViewSet):
    """API endpoint that allows CPE to be viewed or edited."""

    queryset = CPE.objects.all().order_by('id').distinct()
    serializer_class = CPESerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ('vendor', 'product',)
    filterset_class = CPEFilter
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)


class VendorSet(viewsets.ModelViewSet):
    """API endpoint that allows Vendors to be viewed or edited."""

    serializer_class = VendorSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('name',)
    filterset_class = VendorFilter
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        current_user = self.request.user
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=current_user, org_id=org_id)
        monitored_vendors = org.org_monitoring_list.vendors.all().only('id').values_list('id', flat=True)
        return Vendor.objects.all().prefetch_related(
            'org_monitoring_list', 'product_set'
            ).annotate(
                monitored=Case(
                    When(id__in=monitored_vendors, then=True),
                    default=False,
                    output_field=BooleanField()
                ),
                products_count=Count('product')
            ).order_by('-name').distinct()


class ProductSet(viewsets.ModelViewSet):
    """API endpoint that allows Products to be viewed or edited."""

    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('name')
    filterset_class = ProductFilter
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        current_user = self.request.user
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=current_user, org_id=org_id)
        monitored_products = list(org.org_monitoring_list.products.only('id').values_list('id', flat=True))
        return Product.objects.all().prefetch_related(
            'vendor', 'org_monitoring_list__products', 'org_monitoring_list',
            # 'vulns'
            ).annotate(
                monitored=Case(
                    When(id__in=monitored_products, then=True),
                    default=False,
                    output_field=BooleanField()
                ),
                # vulns_count=Count('vulns')
            ).order_by('-name').distinct()


class ProductDetailSet(viewsets.ModelViewSet):
    """API endpoint that allows ProductDetails to be viewed or edited."""

    serializer_class = ProductDetailSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('name')
    filterset_class = ProductDetailFilter
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        current_user = self.request.user
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=current_user, org_id=org_id)

        monitored_products = org.org_monitoring_list.products.all()
        return Product.objects.all().prefetch_related(
            'vendor', 'org_monitoring_list__products', 'org_monitoring_list',
            'productversion_set'
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

    def get_permissions(self):
        return get_api_default_permissions(self)


class BulletinSet(viewsets.ModelViewSet):
    """API endpoint that allows Bulletin to be viewed or edited."""

    queryset = Bulletin.objects.all().order_by('id')
    serializer_class = BulletinSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BulletinFilter
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)


class PackageSet(viewsets.ModelViewSet):
    """API endpoint that allows Package to be viewed or edited."""

    # queryset = Package.objects.all().order_by('name')
    serializer_class = PackageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PackageFilter
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        current_user = self.request.user
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=current_user, org_id=org_id)
    
        monitored_packages = org.org_monitoring_list.packages.all()

        return Package.objects.all().prefetch_related('type', 'vulns').annotate(
                monitored=Case(
                    When(id__in=monitored_packages, then=True),
                    default=False,
                    output_field=BooleanField()
                )
            ).order_by('-name').distinct()


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_cwes(self):
    cwes = CWESerializer(CWE.objects.all().order_by('cwe_id'), many=True).data
    return JsonResponse(cwes, safe=False)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_cwes(self):
    cwes = CWESerializer(CWE.objects.all().order_by('cwe_id'), many=True).data
    return JsonResponse(cwes, safe=False)


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
    sync_cve_task.apply_async(args=[cve_id], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


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
def sync_cves_fromyear_async(self, from_year):
    # sync_cves_fromyear_task.apply_async(args=[from_year], queue='default', retry=False)
    sync_cves_task.apply_async(args=[from_year], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sync_cves_atyear_async(self, year):
    # sync_cves_atyear_task.apply_async(args=[year], queue='default', retry=False)
    sync_cves_task.apply_async(args=[year, year], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)

#
# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def sync_cves_atyear_async_bis(self, year):
#     sync_cves_atyear_task_bis.apply_async(args=[year], queue='default', retry=False)
#     return JsonResponse("enqueued.", safe=False)

#
# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def sync_cves_atyear_async_bis(self, year):
#     sync_cves_atyear_task_bis.apply_async(args=[year], queue='default', retry=False)
#     return JsonResponse("enqueued.", safe=False)


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
@permission_classes([IsAuthenticated])
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
