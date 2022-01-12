from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import viewsets
from vulns.models import Vuln
from common.utils import organization
from .models import VPRating, VPR_METRICS
from .serializers import VPRatingSerializer
from .utils import _refresh_vprating, _calc_vprating
from datetime import datetime, date
from itertools import chain

class VPRatingSet(viewsets.ModelViewSet):
    """API endpoint that allows ratings to be viewed or edited."""

    queryset = VPRating.objects.all().order_by('-updated_at')
    serializer_class = VPRatingSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vprating_metrics(self):
    return JsonResponse(VPR_METRICS)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vuln_vector(self, vuln_id):

    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    today_date = date.today()

    # Vulnerability
    vector = "" + vuln.cvss_vector

    if vuln.is_confirmed is True:
        vector += "/CL:Y"

    if type(vuln.published) is datetime:
        published_date = vuln.published.date()
        delta = today_date - published_date
        vector += "/VX:" + str(delta.days)

    ea_metrics = ['unknown', 'private', 'public']
    em_metrics = ['unknown', 'unproven', 'poc', 'functional']
    et_metrics = ['unknown', 'low', 'medium', 'high', 'trusted']
    ea_idx = ea_max_idx = 0
    em_idx = em_max_idx = 0
    et_idx = et_max_idx = 0
    ex_max_days = 0

    exploits = list(
        chain(
            vuln.exploitmetadata_set.all(),
            vuln.orgexploitmetadata_set.filter(organization=org)
        )
    )

    for exploit in exploits:
        e = model_to_dict(exploit)

        ea_idx = ea_metrics.index(e['availability'])
        if ea_idx > ea_max_idx:
            ea_max_idx = ea_idx

        em_idx = em_metrics.index(e['maturity'])
        if em_idx > em_max_idx:
            em_max_idx = em_idx

        et_idx = et_metrics.index(e['trust_level'])
        if et_idx > et_max_idx:
            et_max_idx = et_idx

        if type(e['published']) is datetime:
            published_date = e['published'].date()
            delta_published_date = today_date - published_date
            if delta_published_date.days > ex_max_days:
                ex_max_days = delta_published_date.days

    ea_vectors = ['X', 'R', 'U']
    em_vectors = ['X', 'U', 'P', 'F']
    et_vectors = ['X', 'L', 'M', 'H', 'H']

    vector += "/EA:" + str(ea_vectors[ea_max_idx])
    vector += "/EM:" + str(em_vectors[em_max_idx])
    vector += "/ET:" + str(et_vectors[et_max_idx])
    vector += "/EX:" + str(ex_max_days)

    if vuln.is_in_the_news:
        vector += "/N:Y"

    if vuln.is_in_the_wild:
        vector += "/W:Y"

    return JsonResponse(vector, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vprating_by_cveid(self, cve_id):
    vuln = get_object_or_404(Vuln, cve_id=cve_id)
    vpr = get_object_or_404(VPRating, vuln=vuln)
    return JsonResponse(model_to_dict(vpr))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def refresh_vprating_by_id(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    vpr = _refresh_vprating(vuln)
    if vpr is not None:
        return JsonResponse(model_to_dict(vpr))
    else:
        return JsonResponse({'error': 'unable to refresh vprating'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    vpr = _calc_vprating(vuln=vuln, asset_metadata=asset_metadata, org=org)
    if vpr is not None:
        return JsonResponse(model_to_dict(vpr))
    else:
        return JsonResponse({'error': 'unable to refresh vprating'})
