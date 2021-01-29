from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.db.models import Case, When, BooleanField
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from common.utils import organization, get_api_default_permissions
from .models import AlertingRule
from .serializers import AlertingRuleSerializer
from .tasks import send_email_message_task
from vulns.models import Vuln
from datetime import datetime, timedelta


# Events
# - New vulnerability found
# - New vulnerability found on monitored products
# - Change detected on vulnerability
# - Change detected on vulnerability on monitored vuln
# - Change detected on vulnerability related to monitored products


class AlertingRuleSet(viewsets.ModelViewSet):
    """API endpoint that allows Alerting rules to be viewed or edited."""

    queryset = AlertingRule.objects.all().order_by('updated_at')
    serializer_class = AlertingRuleSerializer
    filter_backends = (filters.DjangoFilterBackend,)

    def get_permissions(self):
        return get_api_default_permissions(self)


@api_view(['GET'])
def get_monitored_products_report_daily(self):
    org_id = self.session.get('org_id', None)
    org = organization.get_current_organization(user=self.user, org_id=org_id)
    sendmail = False
    if self.GET.get('sendmail', False) and self.GET.get('sendmail') == 'yes':
        sendmail = True
    body = _get_monitored_products_report(org, 1, sendmail)
    return render(self, 'products_report.html', body)


@api_view(['GET'])
def get_monitored_products_report_weekly(self):
    org_id = self.session.get('org_id', None)
    org = organization.get_current_organization(user=self.user, org_id=org_id)
    sendmail = False
    if self.GET.get('sendmail', False) and self.GET.get('sendmail') == 'yes':
        sendmail = True
    body = _get_monitored_products_report(org, 7, sendmail)
    return render(self, 'products_report.html', body)


@api_view(['GET'])
def get_monitored_products_report_monthly(self):
    org_id = self.session.get('org_id', None)
    org = organization.get_current_organization(user=self.user, org_id=org_id)
    sendmail = False
    if self.GET.get('sendmail', False) and self.GET.get('sendmail') == 'yes':
        sendmail = True
    body = _get_monitored_products_report(org, 30, sendmail)
    return render(self, 'products_report.html', body)


@api_view(['GET'])
def get_monitored_products_report_by_days(self, days):
    org_id = self.session.get('org_id', None)
    org = organization.get_current_organization(user=self.user, org_id=org_id)
    sendmail = False
    if self.GET.get('sendmail', False) and self.GET.get('sendmail') == 'yes':
        sendmail = True
    body = _get_monitored_products_report(org, days, sendmail)
    return render(self, 'products_report.html', body)


def _get_monitored_products_report(org, delta_days=1, sendmail=False):
    title = "Products Report"
    monitored_products = org.org_monitoring_list.products.all()

    # Get monitored vulns
    monitored_product_vulns = Vuln.objects.filter(
            products__in=monitored_products,
            updated_at__gte=datetime.now() - timedelta(days=delta_days)
        ).annotate(
            is_new=Case(
                When(created_at__gte=datetime.now() - timedelta(days=delta_days), then=True),
                default=False, output_field=BooleanField()
            )
        )

    monitored_vulns = org.org_monitoring_list.vulns.filter(
        updated_at__gte=datetime.now() - timedelta(days=delta_days)
        ).annotate(
            is_new=Case(
                When(created_at__gte=datetime.now() - timedelta(days=delta_days), then=True),
                default=False, output_field=BooleanField()
            )
        )

    # All vulns
    vulns = monitored_product_vulns.union(monitored_vulns)[:100]

    # Construct summary per product
    products_summary = []
    products_details = {}
    for vuln in vulns:
        for product in vuln.products.all():
            if product not in products_details.keys():
                products_details.update({product.name: []})
            v = vuln.to_dict()
            v['exploit_cnt'] = vuln.exploitmetadata_set.count()+vuln.orgexploitmetadata_set.count()
            v['status'] = 'New'
            if vuln.is_new is False:
                v['status'] = 'Update'
            exploits_list = vuln.exploitmetadata_set.values_list('link', flat=True)
            orgexploits_list = vuln.orgexploitmetadata_set.values_list('link', flat=True)
            v['exploit_links'] = list(set(exploits_list) | set(orgexploits_list))
            # print(v['exploit_links'])
            threats_list = vuln.threatmetadata_set.values_list('link', flat=True)
            orgthreats_list = vuln.orgthreatmetadata_set.values_list('link', flat=True)
            v['threat_links'] = list(set(threats_list) | set(orgthreats_list))
            # print(v['threat_links'])
            products_details[product.name].append(v)

    for product in products_details.keys():
        max_rating = 0
        for vuln in products_details[product]:
            if vuln['score'] > max_rating:
                max_rating = vuln['score']
        for vuln in products_details[product]:
            products_summary.append({
                'vuln_id': vuln['id'],
                'status': vuln['status'],
                'product_name': product,
                'cve': vuln['cveid'],
                'summary': vuln['summary'],
                'cvss': vuln['cvss'],
                'score': vuln['score'],
                'exploit_cnt': vuln['exploit_cnt'],
                'max_rating': max_rating
            })

    body = {
        'products_summary': sorted(products_summary, key=lambda i: (i['max_rating'], i['score'], i['product_name']))[::-1],
        'products_details': products_details,
        'baseurl': settings.BASE_URL
    }

    if sendmail and len(org.org_settings.alerts_emails) > 0:
        send_email_message_task.apply_async(
            args=[title, body, 'products_report', org.org_settings.alerts_emails],
            queue='default',
            retry=False
        )
    return body


@api_view(['GET'])
def send_vuln_update_slack(self, vuln_id):
    # send_slack_message_task.apply_async(
    #         args=[vuln_id, settings.ALERTING_SLACK_APITOKEN, "hears"],
    #         queue='default',
    #         retry=False
    #     )
    from backend_app import slack
    slack.send_slack_message("test", settings.ALERTING_SLACK_APITOKEN, "hears-admin-test")
    return JsonResponse("enqueued.", safe=False)
