from rest_framework import viewsets
from django_filters import rest_framework as filters
from vulns.utils import _refresh_metadata_cve
from .models import MonitoredAsset
from .serializers import MonitoredAssetSerializer


class MonitoredAssetSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assets to be viewed or edited.
    """
    queryset = MonitoredAsset.objects.all().order_by('-updated_at')
    serializer_class = MonitoredAssetSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('name', 'type', 'status')

    # def perform_create(self, serializer):
    #     # print(dir(serializer))
    #     # if serializer.validated_data.get('type') == 'cve':
    #     #     _refresh_metadata_cve(serializer.validated_data.get('name'))
    #     pass
