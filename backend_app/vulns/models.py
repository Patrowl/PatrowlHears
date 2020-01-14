from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField
from simple_history.models import HistoricalRecords
# from monitored_assets.models import MonitoredAsset


def access_default_dict():
    return {
        'authentication': None,
        'complexity': None,
        'vector': None
    }


def impact_default_dict():
    return {
        'availability': None,
        'confidentiality': None,
        'integrity': None
    }


def exploit_info_default_dict():
    return {
        'exploitability_ease': 'No known exploits are available',
        'exploit_available': False,
        'exploit_framework_core': False,
        'exploit_framework_metasploit': False,
        'in_the_news': False
    }

class VulnMetadata(models.Model):
    EXPLOIT_AVAILABILITY = (
        ('unknown', 'No known exploit available'),
        ('private', 'A private exploit is available'),
        ('public', 'A public exploit is available')
    )

    cve_id = models.CharField(max_length=20, null=True)
    summary = models.TextField(default="")
    published = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    assigner = models.CharField(max_length=50, null=True)
    cvss = models.CharField(max_length=5, null=True)
    cvss_time = models.DateTimeField(null=True)
    cvss_vector = models.CharField(max_length=250, null=True)
    cwe = models.CharField(max_length=10, null=True)
    access = JSONField(default=access_default_dict)
    impact = JSONField(default=impact_default_dict)
    vulnerable_products = ArrayField(
        models.CharField(max_length=10, blank=True), null=True)

    is_exploitable = models.BooleanField(default=False)
    exploit_ref = JSONField()
    exploit_info = JSONField(default=exploit_info_default_dict)

    is_confirmed = models.BooleanField(default=False)
    confirm_ref = ArrayField(
        models.CharField(max_length=500, blank=True), null=True)
    # exploit_availability = models.CharField(
    #     max_length=20, choices=EXPLOIT_AVAILABILITY, default='unknown')
    raw = JSONField()

    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "vuln_metadata"

    def __unicode__(self):
        return self.cve_id

    def __str__(self):
        return self.cve_id

    # def clean(self):
    #     pass

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(VulnMetadata, self).save(*args, **kwargs)
