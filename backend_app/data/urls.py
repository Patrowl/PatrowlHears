# -*- coding: utf-8 -*-
from django.urls import path
from . import apis

urlpatterns = [
    path('submit', apis.submit_metadata, name='submit_metadata'),
    path('sync/last', apis.get_last_datasync, name='get_last_datasync'),
    path('sync/info', apis.get_datasync_info, name='get_datasync_info'),
    path('sync/run', apis.run_datasync, name='run_datasync'),
    path('sync/run/async', apis.run_datasync_models_async, name='run_datasync_models_async'),
    path('export/info', apis.export_data_info, name='export_data_info'),
    path('export/model', apis.export_data_model, name='export_data_model'),
    path('export/full', apis.export_data_full, name='export_data_full'),
    path('export/vulns/latest', apis.export_latest_vulns, name='export_latest_vulns'),
    path('import/vulns', apis.import_vulns, name='import_vulns'),
]
