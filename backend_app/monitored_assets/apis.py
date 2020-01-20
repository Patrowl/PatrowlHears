from rest_framework import viewsets
from vulns.utils import _refresh_metadata_cve
from .models import MonitoredAsset
from .serializers import MonitoredAssetSerializer


class MonitoredAssetSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assets to be viewed or edited.
    """
    queryset = MonitoredAsset.objects.all().order_by('-updated_at')
    serializer_class = MonitoredAssetSerializer

    def perform_create(self, serializer):
        # print(dir(serializer))
        if serializer.validated_data.get('type') == 'CVE':
            _refresh_metadata_cve(serializer.validated_data.get('name'))
        pass
