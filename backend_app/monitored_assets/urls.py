# from django.conf.urls import url
from django.urls import path
from . import apis


urlpatterns = [

    # Views
    # path('cve/<asset_name>/info', apis.get_metadata_cve, name='get_metadata_cve'),
    # path('cve/<asset_name>/refresh', apis.refresh_metadata_cve, name='refresh_metadata_cve'),
]
