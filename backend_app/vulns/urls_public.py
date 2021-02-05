from django.urls import path
from . import apis_public


urlpatterns = [
    # path('<vuln_id>/cpes', apis.get_vuln_cpes, name='get_vuln_cpes'),
    path('cve/<cve_id>', apis_public.get_vuln_by_cve, name='get_vulns_by_cve_public'),
    path('<vuln_id>/exploits', apis_public.get_exploits, name='get_exploits_public'),
    path('<vuln_id>/threats', apis_public.get_threats, name='get_threats_public'),
    path('<vuln_id>/export/json', apis_public.export_vuln_json, name='export_vuln_json_public'),
    path('stats', apis_public.get_vuln_stats, name='get_vuln_stats_public'),
    path('latest', apis_public.get_latest_vulns, name='get_latest_vulns_public'),
]
