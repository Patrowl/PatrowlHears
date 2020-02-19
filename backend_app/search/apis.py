from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Q
from rest_framework.decorators import api_view
from vulns.models import Vuln, ExploitMetadata, ThreatMetadata


@api_view(['GET'])
def search_query(self, query):
    results = []
    # vuln_ids = []

    # Search in Vulns
    for vuln in Vuln.objects.filter(
        Q(summary__icontains=query) |
        Q(cve_id__cve_id__icontains=query) |
        Q(reflinks__icontains=query) |
        Q(reflinkids__icontains=query) |
        Q(vulnerable_products__icontains=query)
    ).order_by('updated_at', 'score'):
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
    ):
        results.append({
            'type': 'exploit',
            'value': model_to_dict(exploit)
        })

    # Search in ExploitMetadata
    for threat in ThreatMetadata.objects.filter(
        Q(link__icontains=query) |
        Q(notes__icontains=query)
    ):
        results.append({
            'type': 'threat',
            'value': model_to_dict(threat)
        })
    return JsonResponse(results, safe=False)
