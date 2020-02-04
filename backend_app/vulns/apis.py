from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from common.utils.pagination import StandardResultsSetPagination
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view
from .models import Vuln, ExploitMetadata, ThreatMetadata
from .serializers import (
    VulnSerializer, ExploitMetadataSerializer, ThreatMetadataSerializer,
    VulnFilter, ExploitMetadataFilter)
# from .utils import _refresh_metadata_cve
# from .tasks import refresh_monitored_cves_task


class VulnSet(viewsets.ModelViewSet):
    """API endpoint that allows vuln to be viewed or edited."""

    queryset = Vuln.objects.all().order_by('-updated_at')
    serializer_class = VulnSerializer
    filterset_class = VulnFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination


class ExploitMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows exploit metadata to be viewed or edited."""

    queryset = ExploitMetadata.objects.all().order_by('-updated_at')
    serializer_class = ExploitMetadataSerializer
    filterset_class = ExploitMetadataFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination


class ThreatMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows exploit metadata to be viewed or edited."""

    queryset = ThreatMetadata.objects.all().order_by('-updated_at')
    serializer_class = ThreatMetadataSerializer
    # filterset_class = ThreatMetadataFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination


@api_view(['GET'])
def get_exploits(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    exploits = vuln.exploitmetadata_set.all()
    res = []
    for exploit in exploits:
        res.append(model_to_dict(exploit))
    return JsonResponse(res, safe=False)


@api_view(['GET'])
def get_threats(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    threats = vuln.threatmetadata_set.all()
    res = []
    for threat in threats:
        res.append(model_to_dict(threat))
    return JsonResponse(res, safe=False)

#
# @api_view(['GET'])
# def refresh_metadata_cve(self, cve_id):
#     data = _refresh_metadata_cve(cve_id)
#     return JsonResponse(data, safe=False)
#
#
# @api_view(['GET'])
# def refresh_monitored_cves_async(self):
#     refresh_monitored_cves_task.apply_async(args=[], queue='default', retry=False)
#     return JsonResponse("enqueued", safe=False)
