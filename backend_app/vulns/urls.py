from django.urls import path
from . import apis


urlpatterns = [
    path('<vuln_id>/refresh_scores', apis.refresh_vulns_score_async, name='refresh_vulns_score_async'),
    path('<vuln_id>/history', apis.get_vuln_history, name='get_vuln_history'),
    path('<vuln_id>/exploits', apis.get_exploits, name='get_exploits'),
    path('<vuln_id>/exploits/add', apis.add_exploit, name='add_exploit'),
    path('<vuln_id>/exploits/<exploit_id>/del', apis.del_exploit, name='del_exploit'),
    path('<vuln_id>/threats', apis.get_threats, name='get_threats'),
    path('<vuln_id>/threats/add', apis.add_threat, name='add_threat'),
    path('<vuln_id>/threats/<threat_id>/del', apis.del_threat, name='del_threat'),
    path('stats', apis.get_vuln_stats, name='get_vuln_stats'),
    path('latest', apis.get_latest_vulns, name='get_latest_vulns'),
    # path('cve/<cve_id>/info', apis.get_metadata_cve, name='get_metadata_cve'),
    # path('cve/<cve_id>/refresh', apis.refresh_metadata_cve, name='refresh_metadata_cve'),
    # path('cve/refresh_monitored', apis.refresh_monitored_cves_async, name='refresh_monitored_cves_async'),
]
