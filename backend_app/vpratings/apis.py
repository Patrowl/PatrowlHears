from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import viewsets
from vulns.models import Vuln
from .models import VPRating, VPR_METRICS
from .serializers import VPRatingSerializer
from .utils import _refresh_vprating, _calc_vprating


class VPRatingSet(viewsets.ModelViewSet):
    """API endpoint that allows ratings to be viewed or edited."""

    queryset = VPRating.objects.all().order_by('-updated_at')
    serializer_class = VPRatingSerializer


def get_vprating_metrics(self):
    return JsonResponse(VPR_METRICS)


def get_vprating_by_cveid(self, cve_id):
    vuln = get_object_or_404(Vuln, cve_id=cve_id)
    vpr = get_object_or_404(VPRating, vuln=vuln)
    return JsonResponse(model_to_dict(vpr))


def refresh_vprating_by_id(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    vpr = _refresh_vprating(vuln)
    if vpr is not None:
        return JsonResponse(model_to_dict(vpr))
    else:
        return JsonResponse({'error': 'unable to refresh vprating'})


def refresh_vprating_by_cveid(self, cve_id):
    vuln = get_object_or_404(Vuln, cve_id=cve_id)
    vpr = _refresh_vprating(vuln)
    if vpr is not None:
        return JsonResponse(model_to_dict(vpr))
    else:
        return JsonResponse({'error': 'unable to refresh vprating'})


@api_view(['GET', 'POST'])
def calc_vprating_by_vulnid(self, vuln_id):
    asset_metadata = {}
    if self.method == 'POST':
        asset_metadata.update({
            'exposure': self.data.get('exposure', None),
            'criticality': self.data.get('criticality', None),
            'distribution': self.data.get('distribution', None)
        })

    vuln = get_object_or_404(Vuln, id=vuln_id)
    vpr = _calc_vprating(vuln=vuln, asset_metadata=asset_metadata)
    if vpr is not None:
        return JsonResponse(model_to_dict(vpr))
    else:
        return JsonResponse({'error': 'unable to refresh vprating'})
