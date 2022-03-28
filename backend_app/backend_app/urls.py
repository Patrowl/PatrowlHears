"""backend_app URL Configuration."""
from .adfs import custom_adfs_connection
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from organizations.backends import invitation_backend
from users.backends import CustomRegistrations as invitation_backend
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# from monitored_assets import apis as ma_apis
from alerts import apis as alerts_apis
from vulns import apis as vulns_apis
from vulns import apis_public as vulns_apis_public
from vpratings import apis as vpr_apis
from cves import apis as cves_apis
from users import apis as users_apis
from .views import index

schema_view = get_schema_view(
   openapi.Info(
      title="Patrowl Hears REST-API",
      default_version='v1',
      description="Patrowl Hears REST-API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="getsupport@patrowl.io"),
      license=openapi.License(name="AGPLv3 License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
# router.register(r'api/users', users_apis.OrganizationUserSet, 'users')
router.register(r'api/users', users_apis.UserSet, 'users')
router.register(r'api/org-users', users_apis.OrganizationUserSet, 'org-users')
router.register(r'api/orgs', users_apis.OrganizationSet, 'orgs')
router.register(r'api/alerts', alerts_apis.AlertingRuleSet, 'alerts')
router.register(r'api/vulns', vulns_apis.VulnSet, 'vulns')
router.register(r'api/exploits', vulns_apis.ExploitMetadataSet, 'exploits')
router.register(r'api/org-exploits', vulns_apis.OrgExploitMetadataSet, 'org_exploits')
router.register(r'api/threats', vulns_apis.ThreatMetadataSet, 'threats')
router.register(r'api/org-threats', vulns_apis.OrgThreatMetadataSet, 'org-threats')
router.register(r'api/ratings', vpr_apis.VPRatingSet)
router.register(r'api/kb/cve', cves_apis.CVESet)
router.register(r'api/kb/cpe', cves_apis.CPESet)
router.register(r'api/kb/cwe', cves_apis.CWESet)
router.register(r'api/kb/vendors', cves_apis.VendorSet, 'vendors')
router.register(r'api/kb/products', cves_apis.ProductSet, 'products')
router.register(r'api/kb/detailed-products', cves_apis.ProductDetailSet, 'detailed-products')
router.register(r'api/kb/bulletins', cves_apis.BulletinSet, 'bulletins')
router.register(r'api/kb/packages', cves_apis.PackageSet, 'packages')

# public routes
router.register(r'api/public/vulns', vulns_apis_public.PublicVulnSet, 'vulns-public')

urlpatterns = [
    path('', index, name='index'),
    path('accounts/', include('organizations.urls')),
    path('invitations/', include(invitation_backend().get_urls())),
    path('auth-jwt/obtain_jwt_token/', custom_adfs_connection, name='token_obtain_pair'),
    path('auth-jwt/refresh_jwt_token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth-jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('api/users/', include('users.urls')),
    path('api/search/', include('search.urls')),
    path('api/monitor/', include('monitored_assets.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/vulns/', include('vulns.urls')),
    path('api/public/vulns/', include('vulns.urls_public')),
    path('api/data/', include('data.urls')),
    path('api/ratings/', include('vpratings.urls')),
    path('api/kb/', include('cves.urls')),
    re_path('api/docs/swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    path('oauth2', include('django_auth_adfs.drf_urls')),

]

if settings.DEBUG is True:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns += staticfiles_urlpatterns()

# Add PRO edition urls
if settings.PRO_EDITION:
    try:
        from pro.urls import pro_urlpatterns
        urlpatterns += pro_urlpatterns
    except ImportError as e:
        print(e)
