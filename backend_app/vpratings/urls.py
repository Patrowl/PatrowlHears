from django.urls import path
from . import apis


urlpatterns = [
    # path('cve/<slug:cve_id>/info', apis.get_vprating_by_cveid, name='get_vprating_by_cveid'),
    # path('cve/<slug:cve_id>/refresh', apis.refresh_vprating_by_cveid, name='refresh_vprating_by_cveid'),
    # path('calc/<int:vuln_id>', apis.refresh_vprating_by_id, name='refresh_vprating_by_id'),
    path('calc/<int:vuln_id>', apis.calc_vprating_by_vulnid, name='refresh_vprating_by_id'),
]
