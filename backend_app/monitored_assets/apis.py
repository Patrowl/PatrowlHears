from django.http import JsonResponse
from django.forms.models import model_to_dict
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from common.utils.pagination import StandardResultsSetPagination
from common.utils import organization
# from vulns.utils import _refresh_metadata_cve
# from .models import MonitoredProduct
# from .serializers import MonitoredProductsSerializer
from vulns.models import Vuln
from vulns.serializers import VulnSerializer
from cves.models import CVE, CPE, Bulletin, Vendor, Product
from organizations.models import OrganizationUser, Organization


@api_view(['POST', 'PUT'])
def toggle_monitor_product(self):
    if set(['vendor_name', 'product_name', 'monitored', 'organization_id']).issubset(self.data.keys()) is False:
        return JsonResponse("error.", safe=False, status=500)

    product = Product.objects.filter(
        vendor__name=self.data['vendor_name'], name=self.data['product_name']).first()
    if product is None:
        return JsonResponse("error.", safe=False, status=500)
    else:
        # product.monitored = self.data['monitored']

        organization_id = self.data['organization_id']
        org = organization.get_current_organization(user=self.user, org_id=organization_id)

        if self.data['monitored'] is True and product not in org.org_monitoring_list.products.all():
            org.org_monitoring_list.products.add(product)
        if self.data['monitored'] is False and product in org.org_monitoring_list.products.all():
            org.org_monitoring_list.products.remove(product)
        # if self.data['monitored'] is True and product not in org_user.user_monitoring_list.products.all():
        #     org_user.user_monitoring_list.products.add(product)
        # if self.data['monitored'] is False and product in org_user.user_monitoring_list.products.all():
        #     org_user.user_monitoring_list.products.remove(product)

    product.save()
    return JsonResponse("toggled.", safe=False)


class MonitoredVulnsSet(viewsets.ModelViewSet):
    """
    API endpoint that allows monitored vulns to be viewed or edited.
    """
    queryset = Vuln.objects.order_by('-updated_at')
    # queryset = Vuln.objects.filter(monitored=True).order_by('-updated_at')
    serializer_class = VulnSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('cve_id', 'cvss', 'is_exploitable')
    pagination_class = StandardResultsSetPagination


@api_view(['GET'])
def get_monitored(self):
    filters = self.GET.get('filters', None)
    if filters is not None:
        filters = filters.split(',')
    res = {}
    if filters is None or 'vulns' in filters:
        res_vulns = []
        for vuln in Vuln.objects.filter(monitored=True).order_by('updated_at'):
            res_vulns.append(model_to_dict(vuln))
        res.update({'vulns': res_vulns})
    if filters is None or 'cves' in filters:
        res_cves = []
        for cve in CVE.objects.filter(monitored=True).order_by('updated_at'):
            res_cves.append(model_to_dict(cve))
        res.update({'cves': res_cves})
    # if filters is None or 'cpes' in filters:
    #     res_cpes = []
    #     for cpe in CPE.objects.filter(monitored=True).order_by('updated_at'):
    #         res_cpes.append(model_to_dict(cpe))
    #     res.update({'cpes': res_cpes})
    if filters is None or 'bulletins' in filters:
        res_bulletins = []
        for bulletin in Bulletin.objects.filter(monitored=True).order_by('updated_at'):
            res_bulletins.append(model_to_dict(bulletin))
        res.update({'bulletins': res_bulletins})
    return JsonResponse(res, safe=False)
