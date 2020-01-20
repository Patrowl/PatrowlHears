from django.forms.models import model_to_dict
from vulns.serializers import VulnSerializer
from .models import VPRating
import logging
from cvsslib import cvss2, calculate_vector
logger = logging.getLogger(__name__)


def _refresh_vprating(vuln_id, asset_metadata={}):
    vpr = VPRating.objects.filter(vuln_id=vuln_id).first()
    if vpr is None:
        vpr = VPRating()
    # vuln = vpr.vuln.__dict__
    vuln = VulnSerializer(vpr.vuln).data
    vpr.data = {
        'cve': {
            'published': vuln.get('published', None),
            'modified': vuln.get('modified', None),
            'cvss': vuln.get('cvss', None),
            'cvss_time': vuln.get('cvss_time', None),
            'cvss_vector': vuln.get('cvss_vector', None),
            'cwe': vuln.get('cwe', None),
            'access': vuln.get('access', None),
            'impact': vuln.get('impact', None),
        },
        "exploit": {
            'is_exploitable': vuln.get('is_exploitable', None),
            'references': vuln.get('exploit_ref', None),
            'info': vuln.get('exploit_info', None),
            'trust_ratio': vuln.get('trust_ratio', None),
        },
        "threats": {
            'in_the_wild': vuln.get('in_the_wild', None),
            'in_the_news': vuln.get('in_the_news', None)
        },
        'bulletin': {
            'is_confirmed': vuln.get('is_confirmed', None),
            'confirm_ref': vuln.get('confirm_ref', None)
        },
        'asset': {
            'criticality': asset_metadata.get('criticality', None),
            'exposure': asset_metadata.get('exposure', None)
        }
    }
    vpr.vector = vpr.data['cve']['cvss_vector']

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

    scores = calculate_vector(vpr.vector, cvss2)
    print(scores)
    vpr.score = 0.0
    vpr.save()
    return vpr
