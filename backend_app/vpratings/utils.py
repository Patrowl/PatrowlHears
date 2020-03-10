from django.forms.models import model_to_dict
from .models import VPRating
from cvsslib import cvss2, calculate_vector
import logging
logger = logging.getLogger(__name__)


def _calc_vprating(vuln, asset_metadata={}, save=False):
    # print("_calc_vprating():", vuln)
    vpr = VPRating(vuln=vuln)

    v = vuln.__dict__

    vpr.data = {
        'vulnerability': {
            'published': v.get('published', None),
            'modified': v.get('modified', None),
            'cvss': v.get('cvss', 5.0),
            'cvss_time': v.get('cvss_time', None),
            'cvss_vector': v.get('cvss_vector', None),
            'access': v.get('access', {None}),
            'impact': v.get('impact', {None}),
            'is_confirmed': v.get('is_confirmed', False),
            'remediation': v.get('remediation', False)      # TODO
        },
        "threat": {
            'is_exploitable': v.get('is_exploitable', False),
            'is_in_the_wild': v.get('is_in_the_wild', False),
            'is_in_the_news': v.get('is_in_the_news', False)
        },
        'asset': {
            'criticality': asset_metadata.get('criticality', None),
            'exposure': asset_metadata.get('exposure', None),
            'distribution': asset_metadata.get('distribution', None),
        }
    }

    cvss2adj_vector = ""
    if vpr.data['vulnerability']['cvss_vector'] is not None:
        cvss2adj_vector = vpr.data['vulnerability']['cvss_vector']

    # AdjustTemporal Score
    if vpr.data['threat']['is_exploitable'] not in [None, False]:
        cvss2adj_vector += "/E:H"
    if vpr.data['vulnerability']['is_confirmed'] not in [None, False]:
        cvss2adj_vector += "/RC:C"

    # Adjust Environmental Score
    if vpr.data['asset']['criticality'] is not None:
        if vpr.data['asset']['criticality'] == "high":
            cvss2adj_vector += "/CDP:H"
        elif vpr.data['asset']['criticality'] == "medium":
            cvss2adj_vector += "/CDP:MH"
        elif vpr.data['asset']['criticality'] == "low":
            cvss2adj_vector += "/CDP:LM"
    if vpr.data['asset']['exposure'] is not None:
        if vpr.data['asset']['exposure'] == "internet":
            cvss2adj_vector += "/TD:H"
        elif vpr.data['asset']['exposure'] == "internal":
            cvss2adj_vector += "/TD:M"
        elif vpr.data['asset']['exposure'] == "dmz":
            cvss2adj_vector += "/TD:L"

    vpr.cvssv2adj = calculate_vector(cvss2adj_vector, cvss2)
    vpr.vector = cvss2adj_vector

    vpr.calc_score()
    if save is True:
        vpr.save()
    # print("END: CVSSv2 Adjusted:", vpr.cvssv2adj, "VPRating:", vpr.score)
    return vpr


def _refresh_vprating(vuln_id, asset_metadata={}):
    from vulns.serializers import VulnSerializer
    vpr = VPRating.objects.filter(vuln_id=vuln_id).first()
    if vpr is None:
        vpr = VPRating()
    # vuln = vpr.vuln.__dict__
    vuln = VulnSerializer(vpr.vuln).data
    # exploits = vuln.exploitmetata_set.all()

    vpr.data = {
        'vuln': {
            'published': vuln.get('published', None),
            'modified': vuln.get('modified', None),
            'cvss': vuln.get('cvss', None),
            'cvss_time': vuln.get('cvss_time', None),
            'cvss_vector': vuln.get('cvss_vector', None),
            'access': vuln.get('access', None),
            'impact': vuln.get('impact', None),
            'is_confirmed': vuln.get('is_confirmed', None)
        },
        "threats": {
            'is_exploitable': vuln.get('is_exploitable', None),
            'is_in_the_wild': vuln.get('is_in_the_wild', None),
            'is_in_the_news': vuln.get('is_in_the_news', None)
        },
        'asset': {
            'criticality': asset_metadata.get('criticality', None),
            'exposure': asset_metadata.get('exposure', None),
            'distribution': asset_metadata.get('distribution', None),
        }
    }
    vpr.vector = vpr.data['vuln']['cvss_vector']

    # AdjustTemporal Score
    if vpr.data['exploit']['is_exploitable'] not in [None, False]:
        vpr.vector += "/E:H"
    if vpr.data['bulletin']['is_confirmed'] not in [None, False]:
        vpr.vector += "/RC:C"

    # Adjust Environmental Score
    if vpr.data['asset']['criticality'] is not None:
        if vpr.data['asset']['criticality'] == "high":
            vpr.vector += "/CDP:H"
        elif vpr.data['asset']['criticality'] == "medium":
            vpr.vector += "/CDP:MH"
        elif vpr.data['asset']['criticality'] == "low":
            vpr.vector += "/CDP:LM"
    if vpr.data['asset']['exposure'] is not None:
        if vpr.data['asset']['exposure'] == "internet":
            vpr.vector += "/TD:H"
        elif vpr.data['asset']['exposure'] == "internal":
            vpr.vector += "/TD:M"
        elif vpr.data['asset']['exposure'] == "dmz":
            vpr.vector += "/TD:L"

    adjusted_cvss2_scores = calculate_vector(vpr.vector, cvss2)
    # print("adjusted_cvss2_scores:", adjusted_cvss2_scores)
    # vpr.cvssv2adj = adjusted_cvss2_scores
    vpr.save()
    return vpr
