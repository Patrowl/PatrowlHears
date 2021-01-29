import csv
from django.http import HttpResponse
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from common.utils.pagination import StandardResultsSetPagination
from common.utils import organization
from vulns.models import Vuln
from vulns.serializers import VulnSerializer
from cves.models import CVE, Bulletin, Product, Vendor, Package
from .forms import ImportMonitoredForm


@api_view(['POST', 'PUT'])
def toggle_monitor_product(self):
    if set(['vendor_name', 'product_name', 'monitored', 'organization_id']).issubset(self.data.keys()) is False:
        return JsonResponse("error.", safe=False, status=500)

    product = Product.objects.filter(
        vendor__name=self.data['vendor_name'], name=self.data['product_name']).first()
    if product is None:
        return JsonResponse("error.", safe=False, status=500)
    else:
        organization_id = self.data['organization_id']
        org = organization.get_current_organization(user=self.user, org_id=organization_id)

        if self.data['monitored'] is True and product not in org.org_monitoring_list.products.all():
            org.org_monitoring_list.products.add(product)
        if self.data['monitored'] is False and product in org.org_monitoring_list.products.all():
            org.org_monitoring_list.products.remove(product)

    product.save()
    return JsonResponse("toggled.", safe=False)


@api_view(['POST', 'PUT'])
def toggle_monitor_vendor(self):
    if set(['vendor_name', 'monitored', 'organization_id']).issubset(self.data.keys()) is False:
        return JsonResponse("error.", safe=False, status=500)

    vendor = Vendor.objects.filter(name=self.data['vendor_name']).first()
    if vendor is None:
        return JsonResponse("error.", safe=False, status=500)
    else:
        organization_id = self.data['organization_id']
        org = organization.get_current_organization(user=self.user, org_id=organization_id)

        if self.data['monitored'] is True and vendor not in org.org_monitoring_list.vendors.all():
            org.org_monitoring_list.vendors.add(vendor)
            for product in vendor.product_set.all():
                if self.data['monitored'] is True and product not in org.org_monitoring_list.products.all():
                    org.org_monitoring_list.products.add(product)
        if self.data['monitored'] is False and vendor in org.org_monitoring_list.vendors.all():
            org.org_monitoring_list.vendors.remove(vendor)
            for product in vendor.product_set.all():
                if self.data['monitored'] is False and product in org.org_monitoring_list.products.all():
                    org.org_monitoring_list.products.remove(product)

    vendor.save()
    return JsonResponse("toggled.", safe=False)


@api_view(['POST', 'PUT'])
def toggle_monitor_package(self):
    if set(['package_id', 'monitored', 'organization_id']).issubset(self.data.keys()) is False:
        return JsonResponse("error.", safe=False, status=500)

    package = Package.objects.filter(id=self.data['package_id']).first()
    if package is None:
        return JsonResponse("error.", safe=False, status=500)
    else:
        organization_id = self.data['organization_id']
        org = organization.get_current_organization(user=self.user, org_id=organization_id)

        if self.data['monitored'] is True and package not in org.org_monitoring_list.packages.all():
            org.org_monitoring_list.packages.add(package)
        if self.data['monitored'] is False and package in org.org_monitoring_list.packages.all():
            org.org_monitoring_list.packages.remove(package)

    package.save()
    return JsonResponse("toggled.", safe=False)


@api_view(['GET'])
def export_monitored(self, type):
    if type not in ['vendors', 'products', 'packages', 'vulns', 'all']:
        return JsonResponse("error.", safe=False, status=500)

    org_id = self.session.get('org_id', None)
    org = organization.get_current_organization(user=self.user, org_id=org_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['type', 'value', 'groups'])

    if type in ['vendors', 'all']:
        for vendor in org.org_monitoring_list.vendors.all().order_by('name'):
            writer.writerow(['vendor', vendor.name, ''])
    if type in ['products', 'all']:
        for product in org.org_monitoring_list.products.all().order_by('name'):
            writer.writerow(['product', product.vendor.name + ':' + product.name, ''])
    if type in ['packages', 'all']:
        for package in org.org_monitoring_list.packages.all().order_by('name'):
            writer.writerow(['package', package.type.name + ':' + package.name, ''])
    if type in ['vulns', 'all']:
        for vuln in org.org_monitoring_list.vulns.all().order_by('id'):
            writer.writerow(['vuln', vuln.id, ''])

    return response


@api_view(['POST'])
def import_monitored(self):

    form = ImportMonitoredForm(self.POST, self.FILES)
    if self.FILES:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)

        csv_file = self.FILES['file']
        decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
        records = csv.DictReader(decoded_file, delimiter=',')

        # Header is skiped automatically
        for line in records:
            # print(line)
            # print(line['type'])
            try:
                if line['type'] == 'vendor':
                    vendor = Vendor.objects.filter(name=line['value']).first()
                    if vendor is not None and vendor not in org.org_monitoring_list.vendors.all():
                        org.org_monitoring_list.vendors.add(vendor)
                        print()
                if line['type'] == 'product':
                    vendor_name = line['value'].split(':')[0]
                    product_name = line['value'].split(':')[1]
                    product = Product.objects.filter(vendor__name=vendor_name, name=product_name).first()
                    if product is not None and product not in org.org_monitoring_list.products.all():
                        org.org_monitoring_list.products.add(product)
                if line['type'] == 'package':
                    packagetype_name = line['value'].split(':')[0]
                    package_name = line['value'].split(':')[1]
                    package = Package.objects.filter(type__name=packagetype_name, name=package_name).first()
                    if package is not None and package not in org.org_monitoring_list.packages.all():
                        org.org_monitoring_list.packages.add(package)
                if line['type'] == 'vuln':
                    vuln = Vuln.objects.filter(id=line['value']).first()
                    if vuln is not None and vuln not in org.org_monitoring_list.vulns.all():
                        org.org_monitoring_list.vulns.add(vuln)

            except Exception as e:
                print(e)

    return JsonResponse("imported.", safe=False)


#
#
# class MonitoredVulnsSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows monitored vulns to be viewed or edited.
#     """
#     queryset = Vuln.objects.order_by('-updated_at')
#     serializer_class = VulnSerializer
#     filter_backends = (filters.DjangoFilterBackend,)
#     filterset_fields = ('cve_id', 'cvss', 'is_exploitable')
#     pagination_class = StandardResultsSetPagination

#
# @api_view(['GET'])
# def get_monitored(self):
#     filters = self.GET.get('filters', None)
#     if filters is not None:
#         filters = filters.split(',')
#     res = {}
#     if filters is None or 'vulns' in filters:
#         res_vulns = []
#         for vuln in Vuln.objects.filter(monitored=True).order_by('updated_at'):
#             res_vulns.append(model_to_dict(vuln))
#         res.update({'vulns': res_vulns})
#     if filters is None or 'cves' in filters:
#         res_cves = []
#         for cve in CVE.objects.filter(monitored=True).order_by('updated_at'):
#             res_cves.append(model_to_dict(cve))
#         res.update({'cves': res_cves})
#     # if filters is None or 'cpes' in filters:
#     #     res_cpes = []
#     #     for cpe in CPE.objects.filter(monitored=True).order_by('updated_at'):
#     #         res_cpes.append(model_to_dict(cpe))
#     #     res.update({'cpes': res_cpes})
#     if filters is None or 'bulletins' in filters:
#         res_bulletins = []
#         for bulletin in Bulletin.objects.filter(monitored=True).order_by('updated_at'):
#             res_bulletins.append(model_to_dict(bulletin))
#         res.update({'bulletins': res_bulletins})
#     return JsonResponse(res, safe=False)
