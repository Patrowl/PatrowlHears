import logging
import sys
from pycvesearch import CVESearch

logging.basicConfig(level=logging.INFO)

CVESEARCH_URL = "http://localhost:5000/"


## Todo:
# Search exploits on CVE, CPE and keywords (vendor/products)
# Add feeds:
# - cxsecurity.com
# - google/vulncode-db.com https://github.com/google/vulncode-db/blob/master/README.md
# - Vulners/0day.today (public and private exploits)
# - vFeed
# https://sploitus.com/
# Investigate CVE-2019-5434
# - https://vulners.com/saint/SAINT:FF1CBE38FA4871681735ABCB01546D40
# - cve not found: http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-5434
# ---> http://localhost:5000/cve/CVE-2019-20049
# Investigate https://www.exploit-db.com/exploits/47761



def exploitable(cve_id):
    is_exploitable = False
    exploit_ref = []
    exploit_ref_others = []     # Todo
    exploit_desc = []
    exploit_info = {}

    cve = cvesearh.id(cve_id)
    if not cve:
        return is_exploitable   # CVE ID not found

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

    if 'references' in cve.keys():
        exploit_feeds = [
            "exploit-db.com",
            "github.com", "raw.githubusercontent.com",
            "youtube.com"
        ]
        if 'misc' in cve['references'].keys():
            for link in cve['references']['misc']:
                if link.endswith(".pdf"):
                    exploit_ref.append(link)
                for feed in exploit_feeds:
                    if feed in link:
                        is_exploitable = True
                        exploit_ref.append(link)

    exploit_ref = sorted(set(exploit_ref))
    logging.info(is_exploitable)
    logging.info(exploit_ref)
    logging.info(exploit_desc)
    logging.info(exploit_info)
    return is_exploitable


cvesearh = CVESearch(base_url=CVESEARCH_URL)
try:
    cvesearh.dbinfo()
except Exception:
    logging.error("Unable to access CVE-Search endpoint: %s", CVESEARCH_URL)
    sys.exit(-1)

# with open("monitored-cve.txt") as fp:
#     for line_cve in fp:
#         print("{}".format(line_cve))
#         print(exploitable(line_cve))

# print(exploitable('CVE-2013-4695'))
# print(exploitable('CVE-2014-8674'))
# print(exploitable('CVE-2014-2206'))
print(exploitable('CVE-2016-0792'))
