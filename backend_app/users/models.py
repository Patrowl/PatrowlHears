from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from organizations.models import Organization
from vulns.models import Vuln
from cves.models import Vendor, Product, ProductVersion, Package
from annoying.fields import AutoOneToOneField


class OrgMonitoringList(models.Model):
    organization = AutoOneToOneField(Organization, primary_key=True, on_delete=models.CASCADE, related_name='org_monitoring_list')
    vulns = models.ManyToManyField(Vuln, related_name='org_monitoring_list')
    vendors = models.ManyToManyField(Vendor, related_name='org_monitoring_list')
    products = models.ManyToManyField(Product, related_name='org_monitoring_list')
    productversions = models.ManyToManyField(ProductVersion, related_name='org_monitoring_list')
    packages = models.ManyToManyField(Package, related_name='org_monitoring_list')

    class Meta:
        db_table = "org_monitoring_list"


def slack_dict():
    return {
        'channel': '',
        'webhook': '',
        'url': '',
        'new_vuln': False,
        'update_vuln': False
    }


def thehive_dict():
    return {
        'url': '',
        'apikey': '',
        'new_vuln': False,
        'update_vuln': False
    }


def misp_dict():
    return {
        'url': '',
        'apikey': '',
        'new_vuln': False,
        'update_vuln': False
    }


class OrgSettings(models.Model):
    organization = AutoOneToOneField(
        Organization,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='org_settings')

    # Limitations
    max_users = models.IntegerField(default=0, blank=False, null=True)
    max_monitored_items = models.IntegerField(default=100000, blank=False, null=True)
    max_email_contacts = models.IntegerField(default=3, blank=False, null=True)

    # Alerting
    alerts_emails_enabled = models.BooleanField(default=True)
    alerts_emails = ArrayField(
        models.CharField(max_length=250, blank=True), null=True)
    enable_email_alert_new_vuln = models.BooleanField(default=False)
    enable_email_alert_update_vuln = models.BooleanField(default=False)
    enable_daily_email_report = models.BooleanField(default=False)
    enable_weekly_email_report = models.BooleanField(default=False)
    enable_monthly_email_report = models.BooleanField(default=False)
    enable_instant_email_report_exploitable = models.BooleanField(default=False)
    enable_instant_email_report_cvss = models.BooleanField(default=False)
    enable_instant_email_report_cvss_value = models.FloatField(default=8.0, blank=False, null=True)
    enable_instant_email_report_score = models.BooleanField(default=False)
    enable_instant_email_report_score_value = models.FloatField(default=80, blank=False, null=True)

    alerts_slack_enabled = models.BooleanField(default=False)
    alerts_slack = models.JSONField(default=slack_dict)

    alerts_thehive_enabled = models.BooleanField(default=False)
    alerts_thehive = models.JSONField(default=thehive_dict)

    alerts_misp_enabled = models.BooleanField(default=False)
    alerts_misp = models.JSONField(default=misp_dict)

    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords(
        excluded_fields=['updated_at'],
        cascade_delete_history=True)

    class Meta:
        db_table = "org_settings"

    def get_monitored_items_count(self): #@todo: update this
        return self.max_monitored_items

    def get_monitored_items_left(self):
        return self.get_monitored_items_count() - self.max_monitored_items  #@todo: update this
