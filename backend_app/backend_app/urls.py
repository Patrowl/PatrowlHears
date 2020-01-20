"""backend_app URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from monitored_assets import apis as ma_apis
from vulns import apis as vulns_apis
from vpratings import apis as vpr_apis
from cves import apis as cves_apis


router = routers.DefaultRouter()
router.register(r'api/assets', ma_apis.MonitoredAssetSet)
router.register(r'api/vulns', vulns_apis.VulnSet)
router.register(r'api/exploits', vulns_apis.ExploitMetadataSet)
router.register(r'api/threats', vulns_apis.ThreatMetadataSet)
router.register(r'api/ratings', vpr_apis.VPRatingSet)
router.register(r'api/kb/cve', cves_apis.CVESet)
router.register(r'api/kb/cpe', cves_apis.CPESet)
router.register(r'api/kb/cwe', cves_apis.CWESet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/assets/', include('monitored_assets.urls')),
    path('api/vulns/', include('vulns.urls')),
    path('api/ratings/', include('vpratings.urls')),
    path('api/kb/', include('cves.urls')),
    path('', include(router.urls)),
    # path('', include('pages.urls')),
    # path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]
