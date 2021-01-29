from django.urls import path
from . import apis

# /api/alerts/
urlpatterns = [
    path('products/report-monitored/daily', apis.get_monitored_products_report_daily, name='get_monitored_products_report_daily'),
    path('products/report-monitored/weekly', apis.get_monitored_products_report_weekly, name='get_monitored_products_report_weekly'),
    path('products/report-monitored/monthly', apis.get_monitored_products_report_monthly, name='get_monitored_products_report_monthly'),
    path('products/report-monitored/<int:days>', apis.get_monitored_products_report_by_days, name='get_monitored_products_report_by_days'),
    path('vuln/<vuln_id>/slack', apis.send_vuln_update_slack, name='send_vuln_update_slack'),
    # path('cves/report/weekly', apis.get_dailymail_report_cves, name='get_dailymail_report_cves'),
]
