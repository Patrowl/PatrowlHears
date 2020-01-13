# from django.shortcuts import render
from rest_framework import viewsets
from .models import MonitoredAsset
from .serializers import MonitoredAssetSerializer


class MonitoredAssetSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assets to be viewed or edited.
    """
    queryset = MonitoredAsset.objects.all().order_by('-updated_at')
    serializer_class = MonitoredAssetSerializer


def get_metadata(self):
    pass
