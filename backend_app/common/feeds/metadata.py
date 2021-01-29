from vulns.models import Vuln, ExploitMetadata, ThreatMetadata

import logging
logger = logging.getLogger(__name__)


def import_exploit(data):
    # print(data)
    for cve_id in data['CVE']:
        vuln = Vuln.objects.filter(cveid=cve_id).first()
        if vuln is None:
            return {
                'status': 'error',
                'reason': 'Unknown vulnerability: {}'.format(cve_id)}

        try:
            for sl in list(vuln.exploitmetadata_set.values_list('link', flat=True)):
                if data['view_link'].rstrip('/') in sl.rstrip('/'):
                    return {
                        "status": "error",
                        "reason": "Exploit already related to vulnerability"
                    }
            exploit_data = {
                'vuln_id': vuln.id,
                'publicid': data['id'],
                'link': data['view_link'],
                'notes': "{}\n{}".format(data['title'], data['details']),
                'trust_level': 'trusted',
                'tlp_level': 'white',
                'source': data['source'],
                'availability': 'public',
                'published': data['published_at']
            }
            s = ExploitMetadata(**exploit_data)
            s.save()
        except Exception as e:
            # print(e)
            return {
                "status": "error",
                "reason": "Something goes wrong on ExploitMetadata creation: {}".format(e)
            }
    return {'status': 'success'}
