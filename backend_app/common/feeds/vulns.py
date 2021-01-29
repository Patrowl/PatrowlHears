from django.db.models import Q
from cves.models import CWE, CPE, CVE, Vendor, Product, Package, PackageType
from vulns.models import Vuln, ExploitMetadata, ThreatMetadata
from data.models import DataFeedImport
from common.utils import _json_serial
from tqdm import tqdm
from datetime import datetime
from datetime import date as dtdate
from dateutil import parser as dtparser
import copy
import json
import traceback
import logging
logger = logging.getLogger(__name__)


COMMON_EXPLOIT_FEEDS = [
    "exploit-db",
    "packetstormsecurity.com",
    # "github.com",
    "raw.githubusercontent.com",
    "youtube.com",
    "snyk.io/research/",
    "seebub.org",
    "hackerone.com/reports/",
    "zerodayinitiative.com/blog/"
]


def _get_cpe_products(data):
    products = []
    cpes = {}

    for cpe in data:
        c = cpe.split(':')
        v = c[3]
        p = c[4]
        s = c[5]
        if v not in cpes.keys():
            cpes.update({v: {}})
        if p not in cpes[v].keys():
            cpes[v].update({p: []})
        if s not in cpes[v][p]:
            cpes[v][p].append(s)

    for cpes_vendor in cpes.keys():
        vendor, inv = Vendor.objects.get_or_create(name=cpes_vendor)

        for cpe_product in cpes[cpes_vendor].keys():
            product, inp = Product.objects.get_or_create(name=cpe_product, vendor=vendor)
            products.append(product)

    return products

def _create_vuln(data, packages, cveid=""):
    vuln_data = {
        'cveid': cveid,
        'cvss_vector': data['cvssv2_vector'],
        'cvss3_vector':  data['cvssv3_vector'],
        'summary': '{}\n{}\nSolution: {}'.format(data['title'], data['details'], data['recommendation']),
        # 'exploits': [],
        'feedid': data['id'],
        'is_confirmed':  data['is_confirmed'],
        'is_exploitable': data['is_exploitable'],
        'published': dtparser.parse(data['published_at']),
        'reflinks': data['references'],
        'assigner': data['source']
    }

    cve = CVE.objects.filter(cve_id=cveid).first()
    if cve is not None:
        vuln_data['cve'] = cve.id

    if str(data['cvssv2']).isnumeric():
        vuln_data['cvss'] = float(data['cvssv2'])
    if str(data['cvssv3']).isnumeric():
        vuln_data['cvss3'] = float(data['cvssv3'])

    # Search CWE
    if data['cwe_id'] != "":
        cwe_id = CWE.objects.filter(cwe_id=data['cwe_id']).first()
        if cwe_id is not None:
            vuln_data['cwe'] = cwe_id

    # When no CVSS is set
    if str(data['cvssv2']) == '' and str(data['cvssv3']) == '':
        if data['severity'] == 'critical':
            vuln_data['cvss'] = 10.0
        elif data['severity'] == 'high':
            vuln_data['cvss'] = 8.9
        elif data['severity'] == 'medium':
            vuln_data['cvss'] = 6.9
        elif data['severity'] == 'low':
            vuln_data['cvss'] = 3.9
        else:
            vuln_data['cvss'] = 3.9

    vuln = Vuln(**vuln_data)
    vuln.save()

    for rl in data['references']:
        # Check if it's an exploit
        for feed in COMMON_EXPLOIT_FEEDS:
            if feed in rl:
                vuln.is_exploitable = True
                _new_exploit = {
                    'vuln': vuln,
                    'publicid': 'n/a',
                    'link': rl,
                    'notes': "PoC or exploit found:\n{}".format(rl),
                    'trust_level': 'unknown',
                    'tlp_level': 'white',
                    'source': data['source'],
                    'availability': 'public',
                    'type': 'unknown',
                    'maturity': 'poc',
                    'published': dtdate.today(),
                    'modified': dtdate.today(),
                    'raw': rl
                }
                ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                _new_exploit.update({'hash': ex_hash})
                new_exploit = ExploitMetadata(**_new_exploit)
                new_exploit.save()

    # Packages
    for package_name in packages:
        vuln.packages.add(package_name)

    if len(data['vulnerable_packages'].keys()) > 0:
        vuln.vulnerable_packages_versions = copy.deepcopy(data['vulnerable_packages'])

    # Products (CPE)
    if 'vulnerable_products' in data.keys() and data['vulnerable_products'] is not None:
        vuln.vulnerable_products = data['vulnerable_products']
        for product in _get_cpe_products(data['vulnerable_products']):
            vuln.products.add(product)

        vuln.save()
        vuln.update_product_versions()
    vuln.save()
    return vuln


def _update_vuln(vuln, data, packages, cveid=""):
    if cveid != "" and vuln.cveid == "":
        vuln.cveid = cveid

        cve = CVE.objects.filter(cve_id=cveid).first()
        if cve is not None:
            vuln.cve = cve

    if 'feedid' in data.keys() and vuln.feedid == '':
        vuln.feedid = data['feedid']

    if data['cwe_id'] != "":
        cwe = CWE.objects.filter(cwe_id=data['cwe_id']).first()
        if cwe is not None:
            vuln.cwe = cwe

    if str(data['cvssv2']).isnumeric() and vuln.cvss in [None, 0.0]:
        vuln.cvss = float(data['cvssv2'])
    if str(data['cvssv3']).isnumeric() and vuln.cvss3 in [None, 0.0]:
        vuln.cvss3 = float(data['cvssv3'])
    if data['cvssv2_vector'] != '' and vuln.cvss_vector == '':
        vuln.cvss_vector = data['cvssv2_vector']
    if data['cvssv3_vector'] != '' and vuln.cvss3_vector == '':
        vuln.cvss3_vector = data['cvssv3_vector']

    if data['is_exploitable'] is True and vuln.is_exploitable is False:
        vuln.is_exploitable = True
    if data['is_confirmed'] is True and vuln.is_confirmed is False:
        vuln.is_confirmed = True

    for ref in data['references']:
        if ref not in vuln.reflinks and ref.rstrip('/') not in vuln.reflinks:
            vuln_reflinks = list(vuln.reflinks)
            vuln_reflinks.append(ref)
            vuln.reflinks = sorted(list(set(vuln_reflinks)))

            # Check if it's an exploit
            for feed in COMMON_EXPLOIT_FEEDS:
                if feed in ref and vuln.exploitmetadata_set.filter(link=ref).exists() is False:
                    vuln.is_exploitable = True
                    _new_exploit = {
                        'vuln': vuln,
                        'publicid': 'n/a',
                        'link': ref,
                        'notes': "PoC or exploit found:\n{}".format(ref),
                        'trust_level': 'unknown',
                        'tlp_level': 'white',
                        'source': data['source'],
                        'availability': 'public',
                        'type': 'unknown',
                        'maturity': 'poc',
                        'published': dtdate.today(),
                        'modified': dtdate.today(),
                        'raw': ref
                    }
                    ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                    _new_exploit.update({'hash': ex_hash})
                    new_exploit = ExploitMetadata(**_new_exploit)
                    new_exploit.save()

    # vulnerable_packages
    for package_name in packages:
        if package_name not in vuln.packages.all():
            vuln.packages.add(package_name)

    if len(data['vulnerable_packages'].keys()) > 0:
        vuln.vulnerable_packages_versions = {
            **vuln.vulnerable_packages_versions,
            **data['vulnerable_packages']
        }

    # vulnerable_products
    if 'vulnerable_products' in data.keys() and data['vulnerable_products'] is not None and len(data['vulnerable_products']) > 0:

        if vuln.vulnerable_products is not None and len(vuln.vulnerable_products) > 0:
            vvp = vuln.vulnerable_products.extend(data['vulnerable_products'])
        else:
            vvp = data['vulnerable_products']

        if vvp is not None and len(vvp) > 0:
            vuln.vulnerable_products = sorted(list(set(vvp)))
        else:
            vuln.vulnerable_products = []

        for product in _get_cpe_products(data['vulnerable_products']):
            if product not in vuln.products.all():
                vuln.products.add(product)

        vuln.save()
        vuln.update_product_versions()

    vuln.save()
    return vuln


def import_feedvuln(data, filename, filename_hash):
    # print(filename, data['CVE'], filename_hash)
    """
    1. Check if a vulnerability exists
        Search by CVE

    if exists, update:
        - references and exploits
        - packages info
        - cvss info
        - is_exploitable/is_confirmed
    """

    packages = []
    if len(data['vulnerable_packages'].keys()) > 0:
        # Create PackageType or Package if not exists
        for dpt in data['vulnerable_packages'].keys():
            package_type, pts = PackageType.objects.get_or_create(name=dpt)

            for dpn in data['vulnerable_packages'][dpt].keys():
                package_name, pns = Package.objects.get_or_create(type=package_type, name=dpn)
                packages.append(package_name)


    if len(data['CVE']) == 0:
        # No CVE is set. Check if a related FeedID is already known, create a new vuln otherwise
        try:
            vuln = Vuln.objects.filter(feedid=data['id']).first()
            if vuln is None:
                # print('NOCVE: New vulnerability ? check DataFeedImport/object_id. Otherwise, create a new one yeeehaaaa')
                vuln = _create_vuln(data, packages)

            else:
                # print('NOCVE: Existing vulnerability. Attempt to update some fields')
                vuln = _update_vuln(vuln, data, packages)

            if vuln is not None:
                DataFeedImport.objects.create(
                    filename=filename,
                    hash=filename_hash,
                    source=data['source'],
                    type=data['type'],
                    object_id=vuln.id
                )

        except Exception as e:
            print(e)
            traceback.print_exc()
    else:
        for cveid in data['CVE']:
            try:
                vuln = Vuln.objects.filter(cveid=cveid).first()
                # vuln = Vuln.objects.filter(Q(cveid=cveid)|Q(feedid=data['id'])).first()
                if vuln is None:
                    # print('New vulnerability ? check DataFeedImport/object_id. Otherwise, create a new one yeeehaaaa')

                    vuln_feedid = Vuln.objects.filter(feedid=data['id']).first()
                    if vuln_feedid is None:
                        # print('Has CVE and FeedID unknown -> Create new vuln')
                        vuln = _create_vuln(data, packages, cveid)

                    else:
                        # print('Has CVE and FeedID known -> Try to update some fields')
                        vuln = _update_vuln(vuln_feedid, data, packages, cveid)
                else:
                    # print('Existing vulnerability. Attempt to update some fields')
                    vuln = _update_vuln(vuln, data, packages, cveid)

                if vuln is not None:
                    DataFeedImport.objects.create(
                        filename=filename,
                        hash=filename_hash,
                        source=data['source'],
                        type=data['type'],
                        object_id=vuln.id
                    )

            except Exception as e:
                print(e)
                traceback.print_exc()

    return


def import_cwes(cwes):
    my_cwes = CWE.objects.values_list('cwe_id', flat=True)
    for cwe in tqdm(cwes, desc='CWES'):
        if 'CWE-'+cwe['id'] not in my_cwes:
            new_cwe = CWE(
                cwe_id="CWE-"+cwe['id'],
                name=cwe['name'],
                description=cwe['description']
            )
            new_cwe.save()
            # print("New CWE added: {}".format(new_cwe.cwe_id))

    return


def import_cpes(data):
    my_cpes = list(CPE.objects.values_list('vector', flat=True))
    for vendor_name in tqdm(data.keys(), desc='CPES'):
        vendor, inv = Vendor.objects.get_or_create(name=vendor_name)

        product_cpes = []

        for product_name in data[vendor_name].keys():
            product, inp = Product.objects.get_or_create(name=product_name, vendor=vendor)

            # product_cpes = []
            for cpe_vector in data[vendor_name][product_name].keys():
                if cpe_vector not in my_cpes:
                    try:
                        c = CPE(
                            vector=cpe_vector,
                            title=data[vendor_name][product_name][cpe_vector],
                            product=product,
                            vendor=vendor
                        )
                        product_cpes.append(c)
                        my_cpes.append(cpe_vector)
                    except Exception as e:
                        logger.error(e)
                        pass

        CPE.objects.bulk_create(product_cpes)

    return True


def import_cpe(vector, title, product, vendor):
    # if CPE.objects.filter(vector=vector).exists() is False:
    try:
        CPE.objects.get_or_create(
            vector=vector,
            title=title,
            product_id=product,
            vendor_id=vendor
        )
        # print("New CPE added: {}".format(vector))
    except Exception as e:
        # print(e)
        logger.error(e)
        return False
    return True


def sync_vuln_fromcve(cve):
    # print(cve.vulnerable_products)
    _vuln_data = {
        'cve': cve,
        'cveid': cve.cve_id,
        'summary': cve.summary,
        'published': cve.published,
        'modified': cve.modified,
        'assigner': cve.assigner,
        'is_confirmed': True,
        'cvss': cve.cvss,
        'cvss_time': cve.cvss_time,
        'cvss_vector': cve.cvss_vector,
        'cvss_version': cve.cvss_version,
        'cvss_metrics': cve.cvss_metrics,
        'cvss3': cve.cvss3,
        'cvss3_vector': cve.cvss3_vector,
        'cvss3_version': cve.cvss3_version,
        'cvss3_metrics': cve.cvss3_metrics,
        'cwe': cve.cwe,
        'vulnerable_products': cve.vulnerable_products,
        'access': cve.access,
        'impact': cve.impact
    }
    vuln = Vuln.objects.filter(cve=cve).first()
    if vuln is None:
        vuln = Vuln(**_vuln_data)
        vuln.save()
    else:
        has_update = False
        for v in _vuln_data.keys():
            if _vuln_data[v] != getattr(vuln, v):
                has_update = True
                setattr(vuln, v, _vuln_data[v])
        if has_update is True:
            vuln.save()

    # Sync Products & Product versions
    for cp in cve.products.all():
        if cp not in vuln.products.all():
            vuln.products.add(cp)

    # Sync exploits tag from cve.references
    reflinks = []
    for ref in cve.references['others']:
        reflinks.append(ref['url'])
        if 'Exploit' in ref['tags']:
            vuln.is_confirmed = True
            vuln.is_exploitable = True
            ex = ExploitMetadata.objects.filter(vuln=vuln, link=ref['url']).first()
            if ex is None:
                new_exploit_data = {
                    'vuln': vuln,
                    'publicid': 'n/a',
                    'link': ref['url'],
                    'notes': "Synced from NVD",
                    'trust_level': 'trusted',
                    'tlp_level': 'white',
                    'source': 'nvd',
                    'availability': 'public',
                    'type': 'exploitation',
                    'maturity': 'unknown',
                    # 'published': e_pubdate,
                    # 'modified': e_update,
                    'raw': ref
                }
                new_exploit = ExploitMetadata(**new_exploit_data)
                new_exploit.save()

    vuln.reflinks = sorted(list(set(reflinks)))

    # Update product versions
    vuln.update_product_versions()

    # Save all
    vuln.save()

    # sync_exploits_fromvia(vuln.id)
    return vuln


def import_cve(data, last_update=None):
    # Create / update CVE
    # Create / update VIA references
    # Create / update VULN
    # Create / update Exploits
    # Create / update Threats

    # Prepare it
    try:
        new_cve = {
            'cve_id': data['cve']['CVE_data_meta']['ID'],
            'summary': data['cve']['description']['description_data'][0]['value'],
            'published': datetime.strptime(data['publishedDate'], '%Y-%m-%dT%H:%MZ'),
            'modified': datetime.strptime(data['lastModifiedDate'], '%Y-%m-%dT%H:%MZ'),
            'assigner': data['cve']['CVE_data_meta']['ASSIGNER'],
            # 'is_confirmed': True,
            'vulnerable_products': [],
            'references': {'others': data['cve']['references']['reference_data']},
            'access': {
                'vector': None,
                'complexity': None,
                'authentication': None,
            },
            'impact': {
                'confidentiality': None,
                'integrity': None,
                'availability': None,
            },
        }

        # CVSS v2 and v3
        if 'baseMetricV2' in data['impact'].keys():
            new_cve.update({
                'cvss': data['impact']['baseMetricV2']['cvssV2']['baseScore'],
                'cvss_time': datetime.strptime(data['lastModifiedDate'], '%Y-%m-%dT%H:%MZ'),
                'cvss_vector': data['impact']['baseMetricV2']['cvssV2']['vectorString'],
                'cvss_version': data['impact']['baseMetricV2']['cvssV2']['version'],
                'cvss_metrics': data['impact']['baseMetricV2'],
                'access': {
                    'vector': data['impact']['baseMetricV2']['cvssV2']['accessVector'],
                    'complexity': data['impact']['baseMetricV2']['cvssV2']['accessComplexity'],
                    'authentication': data['impact']['baseMetricV2']['cvssV2']['authentication'],
                },
                'impact': {
                    'confidentiality': data['impact']['baseMetricV2']['cvssV2']['confidentialityImpact'],
                    'integrity': data['impact']['baseMetricV2']['cvssV2']['integrityImpact'],
                    'availability': data['impact']['baseMetricV2']['cvssV2']['availabilityImpact'],
                },
            })
        if 'baseMetricV3' in data['impact'].keys():
            c = data['impact']['baseMetricV3']
            new_cve.update({
                'cvss3': c['cvssV3']['baseScore'],
                'cvss3_vector': c['cvssV3']['vectorString'],
                'cvss3_version': c['cvssV3']['version'],
                'cvss3_metrics': c,
            })
            # Override some Impact and Access metrics with CVSSv3 metrics if exists
            if '/C:H' in c['cvssV3']['vectorString']:
                new_cve['impact']['confidentiality'] = 'COMPLETE'
            if '/I:H' in c['cvssV3']['vectorString']:
                new_cve['impact']['integrity'] = 'COMPLETE'
            if '/A:H' in c['cvssV3']['vectorString']:
                new_cve['impact']['availability'] = 'COMPLETE'
            if 'attackComplexity' in c['cvssV3'].keys():
                new_cve['access']['complexity'] = c['cvssV3']['attackComplexity']

        # Set CWE
        if 'problemtype_data' in data['cve']['problemtype'].keys():
            for pbs in data['cve']['problemtype']['problemtype_data']:
                for desc in pbs['description']:
                    if desc['value'].startswith('CWE-'):
                        cwe = CWE.objects.filter(cwe_id=desc['value']).first()
                        if cwe is not None:
                            new_cve.update({'cwe': cwe})

        # Set vulnerable products (CPE vectors)
        for node in data['configurations']['nodes']:
            if 'children' in node.keys():
                # print(node['children'])
                for child in node['children']:
                    if 'cpe_match' in child.keys():
                        for cpe_match in child['cpe_match']:
                            new_cve['vulnerable_products'].append(cpe_match['cpe23Uri'])
                            # if 'vulnerable' in cpe_match.keys() and cpe_match['vulnerable'] is True:
                            #     new_cve['vulnerable_products'].append(cpe_match['cpe23Uri'])

            else:
                for cpe_match in node['cpe_match']:
                    new_cve['vulnerable_products'].append(cpe_match['cpe23Uri'])
                    # if 'vulnerable' in cpe_match.keys() and cpe_match['vulnerable'] is True:
                    #     new_cve['vulnerable_products'].append(cpe_match['cpe23Uri'])

    except Exception as e:
        print(e)
        logger.error(e)
        return

    # print("b4 check updates", new_cve['vulnerable_products'])

    # Check updates
    cur_cve = CVE.objects.filter(cve_id=new_cve['cve_id']).first()
    if cur_cve is None:
        # Create new CVE
        try:

            cur_cve = CVE(**new_cve)
            cur_cve.save()
        except Exception as e:
            # print(e)
            logger.error(e)
            return
    else:
        # Update CVE
        has_update = False
        for v in new_cve.keys():
            if new_cve[v] != getattr(cur_cve, v):
                has_update = True
                setattr(cur_cve, v, new_cve[v])
        if has_update is True:
            cur_cve.save()

    # Update Products
    try:
        cpes = {}
        for cpe in cur_cve.vulnerable_products:
            c = cpe.split(':')
            v = c[3]
            p = c[4]
            s = c[5]
            if v not in cpes.keys():
                cpes.update({v: {}})
            if p not in cpes[v].keys():
                cpes[v].update({p: []})
            if s not in cpes[v][p]:
                cpes[v][p].append(s)

        for cpes_vendor in cpes.keys():
            vendor, inv = Vendor.objects.get_or_create(name=cpes_vendor)

            for cpe_product in cpes[cpes_vendor].keys():
                product, inp = Product.objects.get_or_create(name=cpe_product, vendor=vendor)
                if product.id not in cur_cve.products.all().only('id').values_list('id', flat=True):
                    cur_cve.products.add(product)
    except Exception as e:
        # print(e)
        logger.error(e)

    cur_cve.save()
    # print(cur_cve.vulnerable_products)

    sync_vuln_fromcve(cur_cve)
    return


def import_vias(data, last_update=None):
    # Loop over CVES and import/parse data
    for cve_id in data.keys():
        try:
            if isinstance(data[cve_id], dict):
                sync_exploits_fromvia(cve_id, data[cve_id])
        except Exception as e:
            logger.error("'{}': refs: {}".format(cve_id, data[cve_id]))

    return


def sync_exploits_fromvia(cve_id, refs):

    if isinstance(refs, dict) is False:
        return True

    vuln = Vuln.objects.prefetch_related('cve').filter(cveid=cve_id).first()
    if vuln is None:
        return False
    logger.debug("Syncing vuln '{}' --> '{}'".format(vuln, vuln.cve_id))

    reflinks = []
    reflinkids = {}
    exploit_links = list(vuln.exploitmetadata_set.values_list('link', flat=True))

    # Others (from the CVE bulletin)
    if vuln.cve is not None and vuln.cve.references is not None:
        try:
            refs.update(vuln.cve.references)
        except Exception as e:
            logger.error("'{}/{}': refs: {}".format(vuln, cve_id, refs))

    ## Exploit-DB
    if 'exploit-db' in refs.keys():
        vuln.is_exploitable = True
        vuln.is_confirmed = True
        for e in refs['exploit-db']:
            if type(e) == str:
                exploitdb_id = e
                ex_link = 'https://www.exploit-db.com/exploits/{}'.format(exploitdb_id)
                if ex_link not in exploit_links:
                    _new_exploit = {
                        'vuln': vuln,
                        'publicid': exploitdb_id,
                        'link': ex_link,
                        'notes': ex_link,
                        'trust_level': 'trusted',
                        'tlp_level': 'white',
                        'source': 'exploit-db',
                        'availability': 'public',
                        'type': 'exploitation',
                        'maturity': 'functional',
                        'published': None,
                        'modified': None,
                        'raw': e
                    }
            else:
                exploitdb_id = e.get('id', None)
                ex_link = 'https://www.exploit-db.com/exploits/{}'.format(exploitdb_id)
                if ex_link not in exploit_links:
                    e_pubdate, e_update = _extract_exploit_dates(e.get('published', None), e.get('modified', None))
                    _new_exploit = {
                        'vuln': vuln,
                        'publicid': exploitdb_id,
                        'link': ex_link,
                        'notes': "{}-{}\n{}".format(e['id'], e.get('title', '-'), e.get('description', '-')),
                        'trust_level': 'trusted',
                        'tlp_level': 'white',
                        'source': 'exploit-db',
                        'availability': 'public',
                        'type': 'exploitation',
                        'maturity': 'functional',
                        'published': e_pubdate,
                        'modified': e_update,
                        'raw': e
                    }
                ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                _new_exploit.update({'hash': ex_hash})

                new_exploit = ExploitMetadata(**_new_exploit)
                new_exploit.save()
                reflinks.append('https://www.exploit-db.com/exploits/{}'.format(exploitdb_id))
                reflinkids.update({'edb': exploitdb_id})
                exploit_links.append(_new_exploit['link'])

    ## Metasploit
    if 'metasploit' in refs.keys():
        vuln.is_exploitable = True
        vuln.is_confirmed = True
        for e in refs['metasploit']:
            ex_link = e.get('source', 'https://github.com/rapid7/metasploit-framework/blob/master/modules/')
            if ex_link not in exploit_links:
                e_pubdate, e_update = _extract_exploit_dates(
                    e.get('published', None), e.get('modified', None)
                )
                _new_exploit = {
                    'vuln': vuln,
                    'publicid': e.get('id', 'n/a'),
                    'link': ex_link,
                    'notes': "{}-{}\n{}\n\nLinks:\n{}".format(
                        e['id'],
                        e.get('title', '-'),
                        e.get('description', '-'),
                        e.get('references', '-')
                    ),
                    'trust_level': 'trusted',
                    'tlp_level': 'white',
                    'source': 'metasploit',
                    'availability': 'public',
                    'type': 'exploitation',
                    'maturity': 'functional',
                    'published': e_pubdate,
                    'modified': e_update,
                    'raw': e
                }
                ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                _new_exploit.update({'hash': ex_hash})
                new_exploit = ExploitMetadata(**_new_exploit)
                new_exploit.save()
                reflinks.extend(e.get('references', []))
                exploit_links.append(_new_exploit['link'])

    ## PacketStorm
    if 'packetstorm' in refs.keys():
        vuln.is_exploitable = True
        vuln.is_confirmed = True
        for e in refs['packetstorm']:
            ex_link = e.get('source', 'https://packetstormsecurity.com')
            if ex_link not in exploit_links:
                e_pubdate, e_update = _extract_exploit_dates(
                    e.get('published', None), e.get('modified', None)
                )
                _new_exploit = {
                    'vuln': vuln,
                    'publicid': e.get('id', 'n/a'),
                    'link': e.get('source', 'https://packetstormsecurity.com'),
                    'notes': "{}-{}\n{}".format(
                        e['id'],
                        e.get('title', '-'),
                        e.get('data source', '-'),
                    ),
                    'trust_level': 'trusted',
                    'tlp_level': 'white',
                    'source': 'packetstorm',
                    'availability': 'public',
                    'type': 'exploitation',
                    'maturity': 'functional',
                    'published': e_pubdate,
                    'modified': e_update,
                    'raw': e
                }
                ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                _new_exploit.update({'hash': ex_hash})

                new_exploit = ExploitMetadata(**_new_exploit)
                new_exploit.save()
                reflinks.append(e.get('source', None))
                reflinks.append(e.get('data source', None))
                exploit_links.append(_new_exploit['link'])

    ## Vulnerability-lab
    if 'vulner lab' in refs.keys():
        vuln.is_exploitable = True
        vuln.is_confirmed = True
        for e in refs['vulner lab']:
            ex_link = e.get('source', 'n/a')
            if ex_link not in exploit_links:
                e_pubdate, e_update = _extract_exploit_dates(
                    e.get('published', None), e.get('modified', None)
                )
                _new_exploit = {
                    'vuln': vuln,
                    'publicid': e.get('id', 'n/a'),
                    'link': e.get('source', 'n/a'),
                    'notes': "{}-{}".format(
                        e['id'],
                        e.get('title', '-')
                    ),
                    'trust_level': 'trusted',
                    'tlp_level': 'white',
                    'source': 'vulnerabilty-lab',
                    'availability': 'public',
                    'type': 'exploitation',
                    'maturity': 'functional',
                    'published': e_pubdate,
                    'modified': e_update,
                    'raw': e
                }
                ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                _new_exploit.update({'hash': ex_hash})

                new_exploit = ExploitMetadata(**_new_exploit)
                new_exploit.save()
                reflinks.append(e.get('source', None))
                exploit_links.append(_new_exploit['link'])

    ## Seebug
    if 'Seebug' in refs.keys():
        for e in refs['Seebug']:
            if e['bulletinFamily'] == 'exploit':

                link = ''
                if 'source' in e.keys():
                    link = e['source']
                elif 'id' in e.keys():
                    ssvid = "https://www.seebug.org/vuldb/ssvid-{}".format(
                        e['id'].split(':')[1]
                    )
                    link = ssvid
                if link not in exploit_links:
                    vuln.is_exploitable = True
                    vuln.is_confirmed = True
                    e_pubdate, e_update = _extract_exploit_dates(
                        e.get('published', None), e.get('modified', None)
                    )
                    _new_exploit = {
                        'vuln': vuln,
                        'publicid': e.get('id', 'n/a'),
                        'link': link,
                        'notes': "{}-{}\n{}".format(
                            e['id'],
                            e.get('title', '-'),
                            e.get('description', '-')
                        ),
                        'trust_level': 'trusted',
                        'tlp_level': 'white',
                        'source': 'seebug',
                        'availability': 'public',
                        'type': 'exploitation',
                        'maturity': 'functional',
                        'published': e_pubdate,
                        'modified': e_update,
                        'raw': e
                    }
                    ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                    _new_exploit.update({'hash': ex_hash})

                    new_exploit = ExploitMetadata(**_new_exploit)
                    new_exploit.save()
                    reflinks.append(link)
                    exploit_links.append(_new_exploit['link'])

    ## Talos
    if 'talos' in refs.keys():
        vuln.is_exploitable = True
        vuln.is_confirmed = True
        for e in refs['talos']:
            if e.get('source', 'n/a') not in exploit_links:
                e_pubdate, e_update = _extract_exploit_dates(
                    e.get('published', None), e.get('modified', None)
                )
                _new_exploit = {
                    'vuln': vuln,
                    'publicid': e.get('id', 'n/a'),
                    'link': e.get('source', 'n/a'),
                    'notes': "{}-{}".format(
                        e['id'],
                        e.get('title', '-')
                    ),
                    'trust_level': 'trusted',
                    'tlp_level': 'white',
                    'source': 'talos',
                    'availability': 'public',
                    'type': 'exploitation',
                    'maturity': 'functional',
                    'published': e_pubdate,
                    'modified': e_update,
                    'raw': e
                }
                ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                _new_exploit.update({'hash': ex_hash})

                new_exploit = ExploitMetadata(**_new_exploit)
                new_exploit.save()
                reflinks.append(e.get('source', None))
                exploit_links.append(_new_exploit['link'])

    ## Nessus DB
    if 'nessus' in refs.keys():
        vuln.is_confirmed = True
        for e in refs['nessus']:
            reflinks.append(e['source'])
            e_pubdate, e_update = _extract_exploit_dates(
                e.get('published', None), e.get('modified', None)
            )
            e_info = {
                'exploit_available': False,
                'exploit_available_from': []
            }
            if 'sourceData' in e.keys():
                if '"exploitability_ease", value:"Exploits are available"' in e['sourceData']:
                    vuln.is_exploitable = True
                    e_info.update({'exploit_available': True})
                if '"exploitability_ease", value:"No exploit is required"' in e['sourceData']:
                    vuln.is_exploitable = True
                    e_info.update({'exploit_available': True})
                if '"exploit_available", value:"true"' in e['sourceData']:
                    vuln.is_exploitable = True
                    e_info.update({'exploit_available': True})
                if '"exploit_framework_core", value:"true"' in e['sourceData']:
                    vuln.is_exploitable = True
                    e_info['exploit_available_from'].append("Core Impact")
                if '"exploit_framework_metasploit", value:"true"' in e['sourceData']:
                    vuln.is_exploitable = True
                    e_info['exploit_available_from'].append("Metasploit")
                if '"exploit_framework_canvas", value:"true"' in e['sourceData']:
                    vuln.is_exploitable = True
                    e_info['exploit_available_from'].append("Canvas")
                if '"exploit_framework_exploithub", value:"true"' in e['sourceData']:
                    vuln.is_exploitable = True
                    e_info['exploit_available_from'].append("ExploitHub")
                if '"exploit_framework_d2_elliot", value:"true"' in e['sourceData']:
                    vuln.is_exploitable = True
                    e_info['exploit_available_from'].append("Elliot")
                if '"in_the_news", value:"true"' in e['sourceData']:
                    vuln.is_in_the_news = True
                if '"exploited_by_malware", value:"true"' in e['sourceData']:
                    vuln.is_in_the_wild = True

            if e_info['exploit_available'] is True:
                _new_exploit = {
                    'vuln': vuln,
                    'publicid': e.get('plugin id', 'n/a'),
                    'link': e.get('source', 'n/a'),
                    'notes': "{}-{}\nFramework(s):{}\n{}".format(
                        e['plugin id'],
                        e.get('title', '-'),
                        ", ".join(e_info['exploit_available_from']),
                        e.get('description', '-')
                    ),
                    'trust_level': 'trusted',
                    'tlp_level': 'white',
                    'source': 'nessus',
                    'availability': 'public',
                    'type': 'exploitation',
                    'maturity': 'functional',
                    'published': e_pubdate,
                    'modified': e_update,
                    'raw': e
                }
                ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                _new_exploit.update({'hash': ex_hash})
                if vuln.exploitmetadata_set.filter(link=_new_exploit['link']).exists() is False:
                    new_exploit = ExploitMetadata(**_new_exploit)
                    new_exploit.save()
                    reflinks.append(e.get('source', None))
                    exploit_links.append(_new_exploit['link'])

    ## THN
    if 'the hacker news' in refs.keys():
        vuln.is_in_the_news = True
        for t in refs['the hacker news']:
            if vuln.threatmetadata_set.filter(link=t.get('source', 'n/a')).exists() is False:
                t_pubdate, t_update = _extract_exploit_dates(
                    t.get('published', None), t.get('modified', None)
                )
                _new_threat = {
                    'vuln': vuln,
                    'link': t.get('source', 'n/a'),
                    'notes': "{}".format(t.get('title', '-')),
                    'trust_level': 'trusted',
                    'tlp_level': 'white',
                    'source': 'the-hacker-news',
                    'is_in_the_news': True,
                    'published': t_pubdate,
                    'modified': t_update,
                    'raw': t
                }
                new_threat = ThreatMetadata(**_new_threat)
                new_threat.save()
                reflinks.append(t.get('source', None))
                exploit_links.append(_new_exploit['link'])

    ## REFMAP
    if 'refmap' in refs.keys() and type(refs['refmap']) == dict:
        reflinkids.update(refs['refmap'])

        # Confirm
        if 'confirm' in refs['refmap'].keys():
            vuln.is_confirmed = True
            for c in refs['refmap']['confirm']:
                reflinks.append(c)

        # SecurityFocus
        if 'bid' in refs['refmap'].keys():
            for b in refs['refmap']['bid']:
                reflinks.append('https://www.securityfocus.com/bid/{}'.format(b))

        # IBM X-Force
        # if 'xf' in refs['refmap'].keys():
        #     for xf in refs['refmap']['xf']:
        #         reflinks.append('https://exchange.xforce.ibmcloud.com/vulnerabilities/{}'.format(xf))

        # misc
        if 'misc' in refs['refmap'].keys():
            for b in refs['refmap']['misc']:
                reflinks.append(b)
                if b.endswith(".pdf") or b.endswith(".py"):
                    if vuln.exploitmetadata_set.filter(link=b).exists() is False:
                        vuln.is_exploitable = True
                        _new_exploit = {
                            'vuln': vuln,
                            'publicid': 'n/a',
                            'link': b,
                            'notes': "PoC or exploit found:\n{}".format(b),
                            'trust_level': 'unknown',
                            'tlp_level': 'white',
                            'source': 'misc',
                            'availability': 'public',
                            'type': 'unknown',
                            'maturity': 'poc',
                            'published': dtdate.today(),
                            'modified': dtdate.today(),
                            'raw': b
                        }
                        ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                        _new_exploit.update({'hash': ex_hash})
                        new_exploit = ExploitMetadata(**_new_exploit)
                        new_exploit.save()
                        exploit_links.append(_new_exploit['link'])

                for feed in COMMON_EXPLOIT_FEEDS:
                    if feed in b and vuln.exploitmetadata_set.filter(link=b).exists() is False:
                        vuln.is_exploitable = True
                        _new_exploit = {
                            'vuln': vuln,
                            'publicid': 'n/a',
                            'link': b,
                            'notes': "PoC or exploit found:\n{}".format(b),
                            'trust_level': 'unknown',
                            'tlp_level': 'white',
                            'source': 'misc',
                            'availability': 'public',
                            'type': 'unknown',
                            'maturity': 'poc',
                            'published': dtdate.today(),
                            'modified': dtdate.today(),
                            'raw': b
                        }
                        ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                        _new_exploit.update({'hash': ex_hash})
                        new_exploit = ExploitMetadata(**_new_exploit)
                        new_exploit.save()
                        exploit_links.append(_new_exploit['link'])

    if 'others' in refs.keys() and type(refs['others']) == list:
        for r in refs['others']:
            for feed in COMMON_EXPLOIT_FEEDS:
                try:
                    if feed in r['url'] and vuln.exploitmetadata_set.filter(link=r['url']).exists() is False:
                        vuln.is_exploitable = True
                        _new_exploit = {
                            'vuln': vuln,
                            'publicid': 'n/a',
                            'link': r['url'],
                            'notes': "PoC or exploit found:\n{}".format(r['url']),
                            'trust_level': 'unknown',
                            'tlp_level': 'white',
                            'source': 'nvd-misc',
                            'availability': 'public',
                            'type': 'unknown',
                            'maturity': 'functional',
                            'published': dtdate.today(),
                            'modified': dtdate.today(),
                            'raw': b
                        }
                        ex_hash = hash(json.dumps(_new_exploit, sort_keys=True, default=_json_serial))
                        _new_exploit.update({'hash': ex_hash})
                        new_exploit = ExploitMetadata(**_new_exploit)
                        new_exploit.save()
                        exploit_links.append(_new_exploit['link'])
                except Exception:
                    pass

    # Update reflinks and reflinkids
    reflinks.extend(vuln.reflinks)
    vuln.reflinks = sorted(list(set(reflinks)))
    vuln.reflinkids.update(reflinkids)
    vuln.save()

    # if sorted(vuln.reflinks) != sorted(list(set(reflinks))) or (not reflinkids.items() <= vuln.reflinkids.items()):
    #     vuln.reflinks = sorted(list(set(reflinks)))
    #     vuln.reflinkids.update(reflinkids)
    #     vuln.save()

    return True


def _extract_exploit_dates(published, modified):
    e_pubdate = published
    e_update = modified
    if e_pubdate is not None:
        try:
            e_pubdate = datetime.strptime(e_pubdate, "%Y-%m-%d").date()
        except Exception:
            e_pubdate = None
    if e_update is not None:
        try:
            e_update = datetime.strptime(e_update, "%Y-%m-%d").date()
        except Exception:
            e_update = None
    else:
        e_update = e_pubdate
    return e_pubdate, e_update
