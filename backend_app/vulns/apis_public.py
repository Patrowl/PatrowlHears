from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.db.models import F
from common.utils.pagination import StandardResultsSetPagination
from common.utils import _json_serial
from common.utils.permissions import ReadOnly
from rest_framework import viewsets, mixins
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view, permission_classes
from .models import (
    Vuln, ExploitMetadata, ThreatMetadata
)
from .serializers import (
    VulnSerializer, VulnFilter,
    ExploitMetadataSerializer,
    ThreatMetadataSerializer
)

from datetime import datetime, timedelta
import json


# class VulnPublicSet(viewsets.ModelViewSet):
class PublicVulnSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint that allows vuln to be viewed without authentication."""

    serializer_class = VulnSerializer
    filterset_class = VulnFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination
    permission_classes = [ReadOnly]

    def get_queryset(self):
        return Vuln.objects.all().prefetch_related('exploitmetadata_set', 'products', 'products__vendor', 'cwe').annotate(exploit_count=F('id')).order_by('-updated_at').distinct()


@api_view(['GET'])
@permission_classes([ReadOnly])
def get_vuln_by_cve(self, cve_id):
    vuln = get_object_or_404(Vuln, cveid=cve_id)
    vuln.exploit_count = vuln.exploitmetadata_set.count()
    vuln_json = VulnSerializer(vuln, context={'request': self}).data
    exploits_json = ExploitMetadataSerializer(vuln.exploitmetadata_set.all(), many=True, context={'request': self}).data
    threats_json = ThreatMetadataSerializer(vuln.threatmetadata_set.all(), many=True, context={'request': self}).data

    res_json = {
        "vulnerability": vuln_json,
        "exploits": exploits_json,
        "threats": threats_json,
    }

    return JsonResponse(res_json, safe=False)


@api_view(['GET'])
@permission_classes([ReadOnly])
def export_vuln_json(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)

    vuln.exploit_count = vuln.exploitmetadata_set.count()
    vuln_json = VulnSerializer(vuln, context={'request': self}).data
    exploits_json = ExploitMetadataSerializer(vuln.exploitmetadata_set.all(), many=True, context={'request': self}).data
    threats_json = ThreatMetadataSerializer(vuln.threatmetadata_set.all(), many=True, context={'request': self}).data

    res_json = {
        "vulnerability": vuln_json,
        "exploits": exploits_json,
        "threats": threats_json,
    }

    response = HttpResponse(json.dumps(res_json, sort_keys=True, indent=4, default=_json_serial), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=hears_vuln_{}.json'.format(vuln.id)
    return response


@api_view(['GET'])
@permission_classes([ReadOnly])
def get_exploits(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    res = []

    # Get public exploits
    for exploit in vuln.exploitmetadata_set.all():
        e = model_to_dict(exploit)
        e['scope'] = 'public'
        e['relevancy_level'] = exploit.get_relevancy_level()
        res.append(e)

    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([ReadOnly])
def get_threats(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    res = []

    # Get public threat
    for threat in vuln.threatmetadata_set.all():
        t = model_to_dict(threat)
        t['scope'] = 'public'
        res.append(t)

    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([ReadOnly])
def get_vuln_stats(self):
    res = {
        'vulns': Vuln.objects.count(),
        'vulns_exploitable': Vuln.objects.filter(is_exploitable=True).count(),
        'exploits': ExploitMetadata.objects.count(),
        'threats': ThreatMetadata.objects.count(),
    }
    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([ReadOnly])
def get_latest_vulns(self):
    MAX_VULNS = 20
    MAX_TIMEDELTA_DAYS = 30
    if self.GET.get('timedelta', None) and self.GET.get('timedelta').isnumeric():
        MAX_TIMEDELTA_DAYS = int(self.GET.get('timedelta'))+30

    vulns = list(Vuln.objects.all()
        .filter(modified__gte=datetime.now() - timedelta(days=MAX_TIMEDELTA_DAYS))
        .only('id', 'cveid', 'summary', 'score')
        .values('id', 'cveid', 'summary', 'score')
        .order_by('-updated_at').distinct()[:MAX_VULNS])

    exploits = []
    exploit_list = list(ExploitMetadata.objects.all().only('id', 'source', 'link', 'trust_level', 'availability', 'maturity').distinct('link', 'updated_at').order_by('-updated_at', 'link')[:MAX_VULNS])
    for exploit in exploit_list:
        exploits.append({
            'source': exploit.source,
            'link': exploit.link,
            'trust_level': exploit.trust_level,
            'scope': 'public',
            'relevancy_level': exploit.get_relevancy_level()
        })

    res = {
        'vulns': vulns,
        'exploits': exploits,
    }
    return JsonResponse(res, safe=False)
