from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import viewsets
from rest_framework.decorators import api_view
from monitored_assets.models import MonitoredAsset
from .models import VulnMetadata
from .serializers import VulnMetadataSerializer
from .utils import _refresh_metadata_cve
from .tasks import refresh_metadata_cve_task, refresh_monitored_cves_task


class VulnMetadataSet(viewsets.ModelViewSet):
    """
    API endpoint that allows metadata to be viewed or edited.
    """
    queryset = VulnMetadata.objects.all().order_by('-updated_at')
    serializer_class = VulnMetadataSerializer


@api_view(['GET'])
def get_metadata_cve(self, cve_id):
    metadata = VulnMetadata.objects.filter(cve_id=cve_id).first()
    if metadata is None:
        return JsonResponse({})
    return JsonResponse(model_to_dict(metadata), safe=False)


@api_view(['GET'])
def refresh_metadata_cve(self, cve_id):
    data = _refresh_metadata_cve(cve_id)
    return JsonResponse(data, safe=False)


@api_view(['GET'])
def refresh_monitored_cves_async(self):
    refresh_monitored_cves_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued", safe=False)
