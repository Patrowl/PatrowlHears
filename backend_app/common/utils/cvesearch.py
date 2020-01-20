from django.conf import settings
from cves.models import CWE, CPE, CVE
from vulns.models import Vuln, ExploitMetadata, ThreatMetadata
from pymongo import MongoClient
from cpe import CPE as _CPE
import requests
import logging
logger = logging.getLogger(__name__)


def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}


def sync_cwe_fromdb(from_date=None):
    cli = MongoClient(
        settings.DATABASES['mongodb']['HOST'],
        settings.DATABASES['mongodb']['PORT'])
    db = cli['cvedb']
    cwes = db.cwe

    my_cwes = CWE.objects.values_list('cwe_id', flat=True)

    for cwe in cwes.find():
        if cwe['id'] not in my_cwes:
            new_cwe = CWE(
                cwe_id="CWE-"+cwe['id'],
                name=cwe['name'],
                description=cwe['Description']
            )
            new_cwe.save()
    return True


def sync_cpe_fromdb(from_date=None):
    cli = MongoClient(
        settings.DATABASES['mongodb']['HOST'],
        settings.DATABASES['mongodb']['PORT'])
    db = cli['cvedb']
    cpes = db.cpe
    my_cpes = CPE.objects.values_list('vector', flat=True)

    for cpe in cpes.find():
        if cpe['cpe_2_2'] not in my_cpes:
            try:
                c = _CPE(cpe['cpe_2_2'])
                new_cpe = CPE(
                    vector=cpe['cpe_2_2'],
                    title=cpe['title'],
                    vendor=c.get_vendor()[0],
                    product=c.get_product()[0],
                    vulnerable_products=[]
                )
                new_cpe.save()
                for p in cpe['cpe_name']:
                    if 'cpe23Uri' in p.keys():
                        new_cpe.vulnerable_products.append(p['cpe23Uri'])
                    else:
                        print(p)

                new_cpe.save()
            except Exception as e:
                logger.error(e)
    return True


def sync_cve_fromdb(from_date=None):
    cli = MongoClient(
        settings.DATABASES['mongodb']['HOST'],
        settings.DATABASES['mongodb']['PORT'])
    db = cli['cvedb']
    cves = db.cves
    vias = db.via4

    for cve in cves.find():
        cur_cve = CVE.objects.filter(cve_id=cve['id']).first()
        if cur_cve is None:
            _new_cve = {
                'cve_id': cve['id'],
                'summary': cve.get('summary', None),
                'published': cve.get('Published', None),
                'modified': cve.get('Modified', None),
                'assigner': cve.get('assigner', None),
                'cvss': cve.get('cvss', None),
                'cvss_time': cve.get('cvss-time', None),
                'cvss_vector': cve.get('cvss-vector', None),
                'access': cve.get('access', None),
                'impact': cve.get('impact', None),
                'vulnerable_products': []
            }
            # Set CWE
            cwe_id = cve.get('cwe', None)
            _cwe = CWE.objects.filter(cwe_id=cwe_id).first()
            if _cwe is not None:
                _new_cve.update({'cwe': _cwe})

            # Set vulnerable products (CPE vectors)
            for vp in cve['vulnerable_configuration']:
                _new_cve['vulnerable_products'].append(vp)
                # if CPE.objects.filter(vector=vp):
                #     print("found!")

            try:
                cur_cve = CVE(**_new_cve)
                cur_cve.save()
            except Exception as e:
                logger.error(e)

        # Update VIA references
        via = vias.find({'id': cur_cve.cve_id})[0]
        if via:
            cur_cve.references = {
                'refmap': via.get('refmap', []),
                'sources': without_keys(via, ['id', 'refmap', '_id'])
            }
            cur_cve.save(update_fields=["references"])

        # TODO: Create or update Vuln (metrics)
        sync_vuln_fromcve(cve=cur_cve)
        # sync_exploits_fromvia(cve=cur_cve)
        # sync_threats_fromvia(cve_id=cur_cve['cve_id'])
        break

    return True


def sync_via_fromdb(from_date=None):
    cli = MongoClient(
        settings.DATABASES['mongodb']['HOST'],
        settings.DATABASES['mongodb']['PORT'])
    db = cli['cvedb']
    vias = db.via4

    my_cves = CVE.objects.values_list('cve_id', flat=True)

    for via in vias.find():
        if via['id'] in my_cves:
            cve = CVE.objects.get(cve_id=via['id'])
            cve.references = {
                'refmap': via.get('refmap', []),
                'sources': without_keys(via, ['id', 'refmap', '_id'])
            }
            cve.save(update_fields=["references"])
            # Create / Update Vuln
            # sync_exploits_fromvia(cve=cve)
            # break
    return True


def sync_exploits_fromvia(vuln_id=None, cve=None, from_date=None):
    if vuln_id is None and cve is None:
        return False
    vuln = None
    if vuln_id is not None:
        vuln = Vuln.objects.filter(id=vuln_id).first()
    elif cve is not None:
        vuln = Vuln.objects.filter(cve_id=cve).first()
    if vuln is None:
        return False
    print("[sync_exploits_fromvia]: TODO")
    return True


def sync_vuln_fromcve(cve):
    print("[sync_vuln_fromcve]: TODO")
    _vuln_data = {
        'cve_id': cve,
        'summary': cve.summary,
        'published': cve.published,
        'modified': cve.modified,
        'assigner': cve.assigner,
        'cvss': cve.cvss,
        'cvss_time': cve.cvss_time,
        'cvss_vector': cve.cvss_vector,
        'cwe': cve.cwe,
        'access': cve.access,
        'impact': cve.impact
    }
    vuln = Vuln.objects.filter(cve_id=cve).first()
    if vuln is None:
        vuln = Vuln(**_vuln_data)
        vuln.save()
    else:
        # _vuln_data.update({'changeReason': 'sync'})
        Vuln.objects.filter(id=vuln.id).update(**_vuln_data)

    return True


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
    if 'refmap' in cve.keys() and 'misc' in cve['refmap'].keys():
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
        # if 'misc' in cve['refmap'].keys():
        for link in cve['references']:
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
