"""backend_app URL Configuration."""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
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
router.register(r'api/kb/vendors', cves_apis.VendorSet, 'vendors')
# router.register(r'api/kb/vendors/<vendor_name>/products', cves_apis.ProductSet, 'products')
router.register(r'api/kb/bulletin', cves_apis.BulletinSet)

urlpatterns = [
    path('auth-jwt/obtain_jwt_token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth-jwt/refresh_jwt_token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth-jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('api/assets/', include('monitored_assets.urls')),
    path('api/vulns/', include('vulns.urls')),
    path('api/ratings/', include('vpratings.urls')),
    path('api/kb/', include('cves.urls')),
    path('', include(router.urls)),
    # path('', include('pages.urls')),
    # path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]

urlpatterns += staticfiles_urlpatterns()
