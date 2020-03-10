from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.db.models import F, Count, Value
from django.db.models.functions import Concat
from common.utils.pagination import StandardResultsSetPagination
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view
from monitored_assets.models import MonitoredProduct
from cves.models import Product
from .models import Vuln, ExploitMetadata, ThreatMetadata
from .serializers import (
    VulnSerializer, ExploitMetadataSerializer, ThreatMetadataSerializer,
    VulnFilter, ExploitMetadataFilter)
# from .utils import _refresh_metadata_cve
from .tasks import refresh_vulns_score_task
from datetime import datetime, timedelta


class VulnSet(viewsets.ModelViewSet):
    """API endpoint that allows vuln to be viewed or edited."""

    # queryset = Vuln.objects.all().annotate(
    #     cve=F('cve_id__cve_id')
    # ).annotate(
    #     exploit_count=Count('exploitmetadata')
    # ).order_by('-updated_at')
    queryset = Vuln.objects.all().prefetch_related('exploitmetadata_set').annotate(
        exploit_count=Count('exploitmetadata')
    ).order_by('-updated_at')
    serializer_class = VulnSerializer
    filterset_class = VulnFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination


class ExploitMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows exploit metadata to be viewed or edited."""

    queryset = ExploitMetadata.objects.all().annotate(
        vp=F('vuln__vulnerable_products')
    ).order_by('-updated_at')
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


HISTORY_IMPORTANT_FIELDS = {
    'vuln': [
        'cvss', 'cvss_vector', 'summary', 'is_exploitable', 'is_confirmed',
        'is_in_the_news', 'is_in_the_wild', 'monitored'
    ],
    'exploit': [
        'link', 'trust_level', 'tlp_level', 'source', 'availability',
        'maturity'
    ],
    'threat': [
        'link', 'trust_level', 'tlp_level', 'source', 'is_in_the_news',
        'is_in_the_news'
    ]
}


def get_history_diffs(item, scope):
    diffs = {}

    record = item.history.earliest()
    diffs.update({
        record.history_date.timestamp(): {
            'date': record.history_date,
            'reason': 'New {} created'.format(scope),
            'changes': ["'{}' has been set to '{}'".format(f, getattr(record, f)) for f in HISTORY_IMPORTANT_FIELDS[scope]],
            'scope': scope
        }
    })
    while True:
        hdiffs = []
        next = record.next_record
        if next is None:
            break
        delta = next.diff_against(record)
        for change in delta.changes:
            hdiffs.append("'{}' changed from '{}' to '{}'".format(change.field, change.old, change.new))
        if len(hdiffs) > 0:
            diffs.update({
                next.history_date.timestamp(): {
                    'date': next.history_date,
                    'reason': 'Change in {}'.format(scope),
                    'changes': hdiffs,
                    'scope': scope
                }
            })
        record = next

    return diffs


@api_view(['GET'])
def get_vuln_history(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    res = {}

    res.update(get_history_diffs(vuln, 'vuln'))

    for exploit in vuln.exploitmetadata_set.all():
        res.update(get_history_diffs(exploit, 'exploit'))
    for threat in vuln.threatmetadata_set.all():
        res.update(get_history_diffs(threat, 'threat'))
    history = []
    for h in sorted(res.keys()):
        history.append(res[h])
    return JsonResponse(history, safe=False)
    # return JsonResponse(res, safe=False)


@api_view(['GET'])
def get_exploits(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    exploits = vuln.exploitmetadata_set.all()
    res = []
    for exploit in exploits:
        res.append(model_to_dict(exploit))
    return JsonResponse(res, safe=False)


@api_view(['POST'])
def add_exploit(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    data = {
        'vuln': vuln,
        'link': self.data['link'],
        'trust_level': self.data['trust_level'],
        'tlp_level': self.data['tlp_level'],
        'source': self.data['source'],
        'availability': self.data['availability'],
        'maturity': self.data['maturity'],
        'modified': self.data['modified']
    }
    new_exploit = ExploitMetadata(**data)
    new_exploit.save()
    return JsonResponse(model_to_dict(new_exploit), safe=False)


@api_view(['GET'])
def del_exploit(self, vuln_id, exploit_id):
    get_object_or_404(Vuln, id=vuln_id)
    exploit = get_object_or_404(ExploitMetadata, id=exploit_id)
    exploit.delete()
    return JsonResponse("deleted", safe=False)


@api_view(['GET'])
def get_threats(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    threats = vuln.threatmetadata_set.all()
    res = []
    for threat in threats:
        res.append(model_to_dict(threat))
    return JsonResponse(res, safe=False)


@api_view(['POST'])
def add_threat(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    data = {
        'vuln': vuln,
        'link': self.data['link'],
        'trust_level': self.data['trust_level'],
        'tlp_level': self.data['tlp_level'],
        'source': self.data['source'],
        'is_in_the_wild': self.data['is_in_the_wild'],
        'is_in_the_news': self.data['is_in_the_news'],
        'modified': self.data['modified']
    }
    new_threat = ThreatMetadata(**data)
    new_threat.save()
    return JsonResponse(model_to_dict(new_threat), safe=False)


@api_view(['GET'])
def del_threat(self, vuln_id, threat_id):
    get_object_or_404(Vuln, id=vuln_id)
    threat = get_object_or_404(ThreatMetadata, id=threat_id)
    threat.delete()
    return JsonResponse("deleted", safe=False)


@api_view(['GET'])
def refresh_vuln_score(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    vuln.update_score()
    vuln.save()
    return JsonResponse(vuln.score, safe=False)


@api_view(['GET'])
def refresh_vulns_score_async(self):
    refresh_vulns_score_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued", safe=False)


@api_view(['GET'])
def get_vuln_stats(self):
    res = {
        'vulns': Vuln.objects.count(),
        'exploits': ExploitMetadata.objects.count(),
        'threats': ThreatMetadata.objects.count(),
        'monitored': Product.objects.filter(monitored=True).count() + Vuln.objects.filter(monitored=True).count()
    }
    return JsonResponse(res, safe=False)


@api_view(['GET'])
def get_latest_vulns(self):
    MAX_VULNS = 20
    MAX_TIMEDELTA_DAYS = 30
    if self.GET.get('timedelta', None) and self.GET.get('timedelta').isnumeric():
        MAX_TIMEDELTA_DAYS = int(self.GET.get('timedelta'))

    vulns = list(Vuln.objects.all()
        .order_by('-updated_at')
        .values('id', 'cveid', 'summary', 'score')[:MAX_VULNS])

    exploits = list(ExploitMetadata.objects.all()
        .order_by('-updated_at')
        .values('source', 'link', 'trust_level')
        .distinct()[:MAX_VULNS])

    # Get monitored vendor/product and concatenate data
    mp = MonitoredProduct.objects.filter(monitored=True).annotate(
        vendorproduct=Concat(Value(':'), F('vendor'), Value(':'), F('product'), Value(':'))
    ).values_list('vendorproduct', flat=True)

    monitored_vulns = Vuln.objects.filter(monitored=True).annotate(
            exploit_count=Count('exploitmetadata')
        ).order_by('-updated_at').values('id', 'cveid', 'summary', 'score', 'exploit_count', 'updated_at', 'is_confirmed')[:MAX_VULNS]

    monitored_vulns_list = list(monitored_vulns)
    for lv in Vuln.objects.exclude(id__in=[o['id'] for o in monitored_vulns]).filter(monitored=False, modified__gte=datetime.now() - timedelta(days=MAX_TIMEDELTA_DAYS)).order_by('-updated_at')[:10000]:
        # Check if vulnerable products are monitored
        if lv.vulnerable_products is not None and len(lv.vulnerable_products) > 0:
            for lvvp in lv.vulnerable_products:
                res = [ele for ele in mp if(ele in lvvp)]
                if bool(res):
                    monitored_vulns_list.append(lv.to_dict())
                    break

    res = {
        'vulns': vulns,
        'exploits': exploits,
        'monitored_vulns': monitored_vulns_list,
        'monitored_products': list(MonitoredProduct.objects.filter(monitored=True).values('vendor', 'product'))
    }
    return JsonResponse(res, safe=False)
