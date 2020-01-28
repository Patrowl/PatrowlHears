# from django.conf.urls import url
from django.urls import path
from . import apis


urlpatterns = [
    path('cwes/sync', apis.sync_cwes, name='sync_cwes'),
    path('cwes/async', apis.sync_cwes_async, name='sync_cwes_async'),
    path('cpes/sync', apis.sync_cpes, name='sync_cpes'),
    path('cpes/async', apis.sync_cpes_async, name='sync_cpes_async'),
    path('cves/sync', apis.sync_cves, name='sync_cves'),
    path('cves/async', apis.sync_cves_async, name='sync_cves_async'),
    path('cve/<slug:cve_id>/sync', apis.sync_cve, name='sync_cve'),
    path('cve/<slug:cve_id>/info', apis.get_cve_info, name='get_cve_info'),
    path('vias/sync', apis.sync_vias, name='sync_vias'),
    path('vias/async', apis.sync_vias_async, name='sync_vias_async'),
    # path('via_exploits/sync', apis.sync_exploits, name='sync_exploits'),
    # path('via_exploits/async', apis.sync_exploits_async, name='sync_exploits_async'),
]
