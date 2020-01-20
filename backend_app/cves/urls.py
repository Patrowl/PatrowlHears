# from django.conf.urls import url
from django.urls import path
from . import apis


urlpatterns = [
    path('sync/cwe', apis.sync_cwes, name='sync_cwes'),
    path('sync/cpe', apis.sync_cpes, name='sync_cpes'),
    path('sync/cve', apis.sync_cves, name='sync_cves'),
    path('async/cwe', apis.sync_cwes_async, name='sync_cwes_async'),
    path('async/cpe', apis.sync_cpes_async, name='sync_cpes_async'),
    path('async/cve', apis.sync_cves_async, name='sync_cves_async'),
]
