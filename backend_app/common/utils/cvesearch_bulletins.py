import datetime


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
                }
                advisories.append(rhsa_adv)

    return advisories
