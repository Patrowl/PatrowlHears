from django.urls import path
from . import apis


urlpatterns = [
    path('cve/<slug:cve_id>/info', apis.get_vprating_by_cveid, name='get_vprating_by_cveid'),
    path('cve/<slug:cve_id>/refresh', apis.refresh_vprating_by_cveid, name='refresh_vprating_by_cveid'),
    path('id/<int:vuln_id>/refresh', apis.refresh_vprating_by_id, name='refresh_vprating_by_id'),
]
