from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import viewsets
# from rest_framework.decorators import api_view
from .models import Vuln, ExploitMetadata, ThreatMetadata
from .serializers import (
    VulnSerializer, ExploitMetadataSerializer, ThreatMetadataSerializer)
# from .utils import _refresh_metadata_cve
# from .tasks import refresh_monitored_cves_task


class VulnSet(viewsets.ModelViewSet):
    """API endpoint that allows vuln to be viewed or edited."""

    queryset = Vuln.objects.all().order_by('-updated_at')
    serializer_class = VulnSerializer


class ExploitMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows exploit metadata to be viewed or edited."""

    queryset = ExploitMetadata.objects.all().order_by('-updated_at')
    serializer_class = ExploitMetadataSerializer


class ThreatMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows exploit metadata to be viewed or edited."""

    queryset = ThreatMetadata.objects.all().order_by('-updated_at')
    serializer_class = ThreatMetadataSerializer

#
# @api_view(['GET'])
# def get_metadata_cve(self, cve_id):
#     metadata = Vuln.objects.filter(cve_id=cve_id).first()
#     if metadata is None:
#         return JsonResponse({})
#     return JsonResponse(model_to_dict(metadata), safe=False)
#
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
