from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from common.utils import cvesearch
from .models import CVE, CPE, CWE, Bulletin
from .serializers import (
    CVESerializer, CPESerializer, CWESerializer, BulletinSerializer,
    CVEFilter
)
from .tasks import (
    sync_cwes_task, sync_cpes_task, sync_cves_task, sync_vias_task,
    sync_bulletins_task
)


class CVESet(viewsets.ModelViewSet):
    """API endpoint that allows CVE to be viewed or edited."""

    queryset = CVE.objects.all().order_by('cve_id')
    serializer_class = CVESerializer
    filterset_class = CVEFilter
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('cve_id', 'cvss')


class CPESet(viewsets.ModelViewSet):
    """API endpoint that allows CPE to be viewed or edited."""

    queryset = CPE.objects.all().order_by('id')
    serializer_class = CPESerializer
    filter_backends = (filters.DjangoFilterBackend,)


class CWESet(viewsets.ModelViewSet):
    """API endpoint that allows CWE to be viewed or edited."""

    queryset = CWE.objects.all().order_by('cwe_id')
    serializer_class = CWESerializer
    filter_backends = (filters.DjangoFilterBackend,)


class BulletinSet(viewsets.ModelViewSet):
    """API endpoint that allows Bulletin to be viewed or edited."""

    queryset = Bulletin.objects.all().order_by('id')
    serializer_class = BulletinSerializer
    filter_backends = (filters.DjangoFilterBackend,)


@api_view(['GET'])
def sync_cwes(self):
    cvesearch.sync_cwes_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_cwes_async(self):
    sync_cwes_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
def sync_cpes(self):
    cvesearch.sync_cpes_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_cpes_async(self):
    sync_cpes_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
def sync_cves(self):
    cvesearch.sync_cves_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_cve(self, cve_id):
    cvesearch.sync_cve_fromdb(cve_id)
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def get_cve_info(self, cve_id):
    cve = get_object_or_404(CVE, cve_id=cve_id)
    return JsonResponse(model_to_dict(cve), safe=False)


@api_view(['GET'])
def sync_cves_async(self):
    sync_cves_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
def sync_vias(self):
    cvesearch.sync_via_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_vias_async(self):
    sync_vias_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)


@api_view(['GET'])
def sync_bulletins(self):
    cvesearch.sync_bulletins_fromdb()
    return JsonResponse("done.", safe=False)


@api_view(['GET'])
def sync_bulletins_async(self):
    sync_bulletins_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued.", safe=False)

#
# @api_view(['GET'])
# def sync_exploits(self):
#     cvesearch.sync_exploits_fromvia()
#     return JsonResponse("done.", safe=False)
