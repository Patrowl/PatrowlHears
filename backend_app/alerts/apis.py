from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.forms.models import model_to_dict
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import AlertingRule
from .serializers import AlertingRuleSerializer
from .tasks import send_email_message_task
from cves.models import CPE, CVE
from vulns.models import Vuln
from vulns.serializers import VulnSerializer


class AlertingRuleSet(viewsets.ModelViewSet):
    """API endpoint that allows Alerting rules to be viewed or edited."""

    queryset = AlertingRule.objects.all().order_by('updated_at')
    serializer_class = AlertingRuleSerializer
    filter_backends = (filters.DjangoFilterBackend,)


@api_view(['GET'])
def get_dailymail_report_vendors(self):
    title = "test"
    vendors_summary = []
    vendors_details = []
    for vendor in CPE.objects.filter(monitored=True):
        print(vendor)
        # vdata = VulnSerializer(vuln).data
        # vsumary = {
        #     'status': 'change'
        # }
        # vendors_details.append(vdata)
    body = {
        # 'vulns_summary': vulns_summary,
        # 'vulns_details': vulns_details,
    }
    # send_email_message_task.apply_async(args=[title, body, 'sync_report'], queue='default', retry=False)
    # return JsonResponse("enqueued.", safe=False)
    return JsonResponse(body, safe=False)
