from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.db.models.functions import Concat
from django.db.models import F, Value
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import AlertingRule
from .serializers import AlertingRuleSerializer
from .tasks import send_email_message_task
from vulns.models import Vuln
from monitored_assets.models import MonitoredProduct
from datetime import datetime, timedelta


class AlertingRuleSet(viewsets.ModelViewSet):
    """API endpoint that allows Alerting rules to be viewed or edited."""

    queryset = AlertingRule.objects.all().order_by('updated_at')
    serializer_class = AlertingRuleSerializer
    filter_backends = (filters.DjangoFilterBackend,)


@api_view(['GET'])
def get_dailymail_report_vendors(self):
    sendmail = False
    if self.GET.get('sendmail', False) and self.GET.get('sendmail') == 'yes':
        sendmail = True
    title = "Daily vulnerabilities"
    products_summary = []
    # {
    #     'status': 'Add',
    #     'vendor': 'Apache',
    #     'product': 'CouchDB',
    #     'max_cvss': 9.3,
    #     'max_ratin': 94,
    #     'exploits': 3
    # }
    last_vulns_monitored = {}

    # Get monitored vendor/product and concatenate data
    mp = MonitoredProduct.objects.filter(monitored=True).annotate(
        vendorproduct=Concat(Value(':'), F('vendor'), Value(':'), F('product'), Value(':'))
    ).values_list('vendorproduct', flat=True)

    # Get last created/updated vulns
    # last_vulns = Vuln.objects.filter(updated_at__gte=datetime(2020, 2, 14))
    last_vulns = Vuln.objects.filter(updated_at__gte=datetime.now() - timedelta(days=1))

    for lv in last_vulns:
        # Check if the vulnerability is monitored
        if lv.monitored is True and lv.vulnerable_products is not None and len(lv.vulnerable_products) > 0:
            for lvvp in lv.vulnerable_products:
                res = [ele for ele in mp if(ele in lvvp)]
                if bool(res):
                    for _product in res:
                        product = _product.split(':')[2]
                        if product not in last_vulns_monitored.keys():
                            last_vulns_monitored.update({product: []})
                        # last_vulns_monitored[product].append(lv)
                        last_vulns_monitored[product].append(lv.to_dict())
                    break

        # Check if vulnerable products are monitored
        elif lv.vulnerable_products is not None and len(lv.vulnerable_products) > 0:
            for lvvp in lv.vulnerable_products:
                res = [ele for ele in mp if(ele in lvvp)]
                if bool(res):
                    for _product in res:
                        product = _product.split(':')[2]
                        if product not in last_vulns_monitored.keys():
                            last_vulns_monitored.update({product: []})
                        # last_vulns_monitored[product].append(lv)
                        last_vulns_monitored[product].append(lv.to_dict())
                    break

    for product in last_vulns_monitored.keys():
        max_rating = 0
        for vuln in last_vulns_monitored[product]:
            if vuln['rating'] > max_rating:
                max_rating = vuln['rating']
        for vuln in last_vulns_monitored[product]:
            products_summary.append({
                'vuln_id': vuln['id'],
                'status': 'New',
                'product_name': product,
                'cve': vuln['cve_id'],
                'summary': vuln['summary'],
                'cvss': vuln['cvss'],
                'rating': vuln['rating'],
                'exploit_cnt': vuln['exploit_cnt'],
                'max_rating': max_rating   # For triage
            })

    body = {
        'products_summary': sorted(products_summary, key=lambda i: (i['max_rating'], i['rating'], i['product_name']))[::-1],
        'products_details': last_vulns_monitored,
        'baseurl': settings.BASE_URL
    }
    if sendmail:
        send_email_message_task.apply_async(
            args=[title, body, 'sync_report'],
            queue='default',
            retry=False
        )
    # return JsonResponse("enqueued.", safe=False)
    return render(self, 'sync_report.html', body)
