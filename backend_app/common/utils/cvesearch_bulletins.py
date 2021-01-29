import datetime
from datetime import datetime as dt
import logging
logger = logging.getLogger(__name__)


def sync_bulletin_redhat(bulletin):
    # RHSA example
    # {
    #   'title': 'RHSA-2008:0031: xorg-x11-server security update (Important)',
    #   'id': 'RHSA-2008:0031',
    #   'severity': 'Important',
    #   'released': '2008-01-18'
    # }
    advisories = []
    if 'advisories' in bulletin.keys():
        for a in bulletin['advisories']:
            if 'rhsa' in a.keys():
                release_date = None
                if 'released' in a['rhsa'].keys():
                    release_date = datetime.datetime.strptime(a['rhsa']['released'], "%Y-%m-%d").date()
                rhsa_adv = {
                    'publicid': a['rhsa'].get('id', None),
                    'title': a['rhsa'].get('title', None),
                    'severity': a['rhsa'].get('severity', None),
                    'published': release_date,
                    'vendor': 'redhat',
                    # 'raw': a['rhsa']
                }
                advisories.append(rhsa_adv)

    return advisories


def sync_bulletin_msbulletin(bulletins):
    # MSBulletin example
    # {
    #   'bulletin_url': None,
    #   'knowledgebase_id': '3025421',
    #   'date': '2015-01-13T00:00:00',
    #   'title': 'Vulnerability in Windows Components Could Allow Elevation of Privilege',
    #   'severity': 'Important',
    #   'bulletin_id': 'MS15-004',
    #   'knowledgebase_url': None,
    #   'impact': 'Elevation of Privilege'
    # }
    advisories = []
    for bulletin in bulletins:
        try:
            release_date = None
            modified_date = None
            publicid = ""
            if 'published' in bulletin.keys():
                # release_date = datetime.datetime.fromisoformat(bulletin['published']).date()
                release_date = dt.fromisoformat(bulletin['published'])
            elif 'date' in bulletin.keys():
                # release_date = datetime.datetime.fromisoformat(bulletin['date']).date()
                release_date = dt.fromisoformat(bulletin['date'])
            if 'modified' in bulletin.keys():
                # modified_date = datetime.datetime.fromisoformat(bulletin['modified'].replace('Z', '')).date()
                modified_date = dt.fromisoformat(bulletin['modified'].replace('Z', ''))

            if 'bulletin_id' in bulletin.keys():
                publicid = bulletin['bulletin_id']
            elif 'knowledgebase_id' in bulletin.keys():
                publicid = bulletin['knowledgebase_id']
            ms_adv = {
                'publicid': publicid,
                'title': bulletin.get('title', None),
                'severity': bulletin.get('severity', None),
                'impact': bulletin.get('impact', None),
                'published': release_date,
                'modified': modified_date,
                'vendor': 'Microsoft',
                # 'raw': bulletin
            }
            advisories.append(ms_adv)
        except Exception as e:
            logger.error(e)

    return advisories
