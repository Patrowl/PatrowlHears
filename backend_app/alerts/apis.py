from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.forms.models import model_to_dict
from django_filters import rest_framework as filters
from rest_framework import viewsets
# from rest_framework.decorators import api_view
from .models import AlertingRule
from .serializers import AlertingRuleSerializer


class AlertingRuleSet(viewsets.ModelViewSet):
    """API endpoint that allows Alerting rules to be viewed or edited."""

    queryset = AlertingRule.objects.all().order_by('cve_id')
    serializer_class = AlertingRuleSerializer
    filter_backends = (filters.DjangoFilterBackend,)

#
# @api_view(['GET'])
# def sync_cwes(self):
#     cvesearch.sync_cwes_fromdb()
#     return JsonResponse("done.", safe=False)
#
#
# @api_view(['GET'])
# def sync_cwes_async(self):
#     sync_cwes_task.apply_async(args=[], queue='default', retry=False)
#     return JsonResponse("enqueued.", safe=False)
