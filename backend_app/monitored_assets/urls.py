from django.urls import path
from . import apis

urlpatterns = [
    path('search', apis.get_monitored, name='get_monitored'),
    # path('products', apis.MonitoredProductSet.as_view({'get': 'list'})),
    path('vulns', apis.MonitoredVulnsSet.as_view({'get': 'list'})),
    path('product/toggle', apis.toggle_monitor_product, name='toggle_monitor_product'),
    
    # Views
    # path('cve/<asset_name>/info', apis.get_metadata_cve, name='get_metadata_cve'),
    # path('cve/<asset_name>/refresh', apis.refresh_metadata_cve, name='refresh_metadata_cve'),
]
