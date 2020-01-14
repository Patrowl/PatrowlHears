from django.conf import settings
import requests
import logging
logger = logging.getLogger(__name__)


def get_cve_references(cve_id):
    is_exploitable = False
    exploit_ref = []
    # exploit_desc = []
    exploit_info = {}
    is_confirmed = False
    confirm_ref = []

    try:
        r = requests.get(settings.CVESEARCH_URL+"/api/cve/"+cve_id)
        cve = r.json()
    except Exception:
        logger.exception("Bad request to CVE-SEARCH")
        return None

    if not cve:
        logger.error("CVE '{}' not found".format(cve_id))
        return None

    ## Exploit-DB
    if 'exploit-db' in cve.keys():
        is_exploitable = True
        for e in cve['exploit-db']:
            exploit_ref.append(e['source'])
    if 'references' in cve.keys():
        for r in cve['references']:
            if 'exploit-db' in r:
                is_exploitable = True
                exploit_ref.append(r)
    if 'refmap' in cve.keys():
        for r in cve['refmap']['misc']:
            if 'exploit-db' in r:
                is_exploitable = True
                exploit_ref.append(r)

    ## Metasploit
    if 'metasploit' in cve.keys():
        is_exploitable = True
        for m in cve['metasploit']:
            exploit_ref.append(m['source'])

    ## PackeStorm
    if 'packetstorm' in cve.keys():
        is_exploitable = True
        for p in cve['packetstorm']:
            exploit_ref.append(p['data source'])
            exploit_ref.append(p['source'])

    ## vulnerability-lab
    if 'vulner lab' in cve.keys():
        is_exploitable = True
        for v in cve['vulner lab']:
            exploit_ref.append(v['source'])

    ## Seebug
    if 'Seebug' in cve.keys():
        for e in cve['Seebug']:
            if e['bulletinFamily'] == 'exploit':
                is_exploitable = True
                if 'source' in e.keys():
                    exploit_ref.append(e['source'])
                elif 'id' in e.keys():
                    ssvid = "https://www.seebug.org/vuldb/ssvid-{}".format(
                        e['id'].split(':')[1]
                    )
                    exploit_ref.append(ssvid)
                # if 'description' in e.keys():
                #     exploit_desc.append(e['description'])

    ## Nessus DB
    if 'nessus' in cve.keys():
        exploit_info.update({
            'exploitability_ease': 'No known exploits are available',
            'exploit_available': False,
            'exploit_framework_core': False,
            'exploit_framework_metasploit': False,
            'in_the_news': False
        })
        for n in cve['nessus']:
            if 'sourceData' in n.keys():
                if '"exploitability_ease", value:"Exploits are available"' in n['sourceData']:
                    is_exploitable = True
                    exploit_info.update({'exploitability_ease': 'Exploits are available'})
                if '"exploitability_ease", value:"No exploit is required"' in n['sourceData']:
                    is_exploitable = True
                    exploit_info.update({'exploitability_ease': 'No exploit is required'})
                if '"exploit_available", value:"true"' in n['sourceData']:
                    is_exploitable = True
                    exploit_info.update({'exploit_available': True})
                if '"exploit_framework_core", value:"true"' in n['sourceData']:
                    is_exploitable = True
                    exploit_info.update({'exploit_framework_core': True})
                if '"exploit_framework_metasploit", value:"true"' in n['sourceData']:
                    is_exploitable = True
                    exploit_info.update({'exploit_framework_metasploit': True})
                if '"in_the_news", value:"true"' in n['sourceData']:
                    exploit_info.update({'in_the_news': True})

            # Todo: Check CVSS score/vector and update value if not set

    if 'references' in cve.keys():
        exploit_feeds = [
            "exploit-db.com",
            "github.com",
            "raw.githubusercontent.com",
            "youtube.com"
        ]
        if 'misc' in cve['refmap'].keys():
            for link in cve['refmap']['misc']:
                if link.endswith(".pdf"):
                    exploit_ref.append(link)
                elif link.endswith(".py"):
                    exploit_ref.append(link)
                for feed in exploit_feeds:
                    if feed in link:
                        is_exploitable = True
                        exploit_ref.append(link)

    if 'refmap' in cve.keys():
        if 'confirm' in cve['refmap'].keys():
            is_confirmed = True
            for link in cve['refmap']['confirm']:
                confirm_ref.append(link)

    return {
        'is_exploitable': is_exploitable,
        'exploit_ref': sorted(set(exploit_ref)),
        'exploit_info': exploit_info,
        'is_confirmed': is_confirmed,
        'confirm_ref': confirm_ref,
        'raw': cve,
        'source': 'cvesearch'
    }
