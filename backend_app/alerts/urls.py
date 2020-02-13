# from django.conf.urls import url
from django.urls import path
from . import apis


urlpatterns = [
    path('vendors/report/daily', apis.get_dailymail_report_vendors, name='get_dailymail_report_vendors'),
    # path('cves/report/weekly', apis.get_dailymail_report_cves, name='get_dailymail_report_cves'),
]
