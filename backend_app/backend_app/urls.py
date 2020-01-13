"""backend_app URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from monitored_assets import apis as ma_apis


router = routers.DefaultRouter()
router.register(r'api/assets', ma_apis.MonitoredAssetSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/assets/', include('monitored_assets.urls')),
    path('', include(router.urls)),
    # path('', include('pages.urls')),
    # path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]
