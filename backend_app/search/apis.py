from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Q
from rest_framework.decorators import api_view
from vulns.models import Vuln, ExploitMetadata, ThreatMetadata


@api_view(['GET'])
def search_query(self, query, ignore_case=False, limit=20):
    results = []
    # vuln_ids = []

    limit = int(self.GET.get('limit', limit))

    # Search in Vulns
    query_lower = str(query.lower())
    query_upper = str(query.upper())
    for vuln in Vuln.objects.prefetch_related('exploitmetadata_set', 'orgexploitmetadata_set', 'products', 'products__vendor', 'productversions', 'cve', 'cwe').filter(
        Q(summary__icontains=query) |
        Q(cveid__contains=query_upper) |
        Q(reflinks__contains=query) |
        # Q(reflinkids__icontains=query) |
        Q(vulnerable_products__icontains=query_lower)
    # ).only(
    #     'id', 'summary', 'cveid', 'score', 'updated_at', 'vulnerable_products',
    #     'is_exploitable', 'is_confirmed', 'is_in_the_news', 'is_in_the_wild',
    #     'cvss', 'cvss_vector'
    ).order_by('-score', '-cveid', '-updated_at', 'summary')[:limit]:
        results.append({
            'type': 'vuln',
            'value': vuln.to_dict()
        })
        # vuln_ids.append(vuln.id)

    # Search in ExploitMetadata
    for exploit in ExploitMetadata.objects.filter(
        Q(publicid__icontains=query) |
        Q(link__icontains=query) |
        Q(notes__icontains=query)
    ).order_by('-updated_at')[:limit]:
        results.append({
            'type': 'exploit',
            'value': model_to_dict(exploit)
        })

    # Search in ExploitMetadata
    for threat in ThreatMetadata.objects.filter(
        Q(link__icontains=query) |
        Q(notes__icontains=query)
    ).order_by('-updated_at')[:limit]:
        results.append({
            'type': 'threat',
            'value': model_to_dict(threat)
        })
    return JsonResponse(results, safe=False)
