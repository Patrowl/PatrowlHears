from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField
from simple_history.models import HistoricalRecords
from cves.models import CVE, CWE


EXPLOIT_AVAILABILITY = (
    ('unknown', 'No known exploit available'),
    ('private', 'A private exploit is available'),
    ('public', 'A public exploit is available')
)

TRUST_LEVELS = (
    ('unknown', 'Unknown'),
    ('low', 'Low'),         # Not tested
    ('medium', 'Medium'),   # Not tested
    ('trusted', 'High'),    # Official source, validated by trusted partners
)

TLP_LEVELS = (
    ('white', 'White'),  # Public
    ('green', 'Green'),  # Internal, could be shared
    ('amber', 'Amber'),  # Internal, shareable with members of their own organization who need to know
    ('red', 'Red'),      # Internal, restrictly shareable
)

EXPLOIT_TYPES = (
    ('unknown', 'Unknown'),
    ('discovery', 'Discovery'),
    ('exploitation', 'Exploitation'),
)

EXPLOIT_MATURITY_LEVELS = (
    ('unknown', 'Unknown'),
    ('unproven', 'Unproven'),
    ('poc', 'PoC'),
    ('functional', 'Functional Exploit'),
)


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


class Vuln(models.Model):
    cve_id = models.ForeignKey(CVE, on_delete=models.CASCADE, null=True)
    summary = models.TextField(default="")
    published = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    assigner = models.CharField(max_length=50, null=True)
    cvss = models.FloatField(default=0.0, null=True)
    cvss_time = models.DateTimeField(null=True)
    cvss_vector = models.CharField(max_length=250, null=True)
    cwe = models.ForeignKey(CWE, on_delete=models.CASCADE, null=True)
    access = JSONField(default=access_default_dict)
    impact = JSONField(default=impact_default_dict)

    is_exploitable = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_in_the_news = models.BooleanField(default=False)
    is_in_the_wild = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "vulns"

    def __unicode__(self):
        return "PH-{}".format(self.id)

    def __str__(self):
        return "PH-{}".format(self.id)

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Vuln, self).save(*args, **kwargs)


# class VulnMetadata(models.Model):
#     cve_id = models.CharField(max_length=20, null=True)
#     summary = models.TextField(default="")
#     published = models.DateTimeField(null=True)
#     modified = models.DateTimeField(null=True)
#     assigner = models.CharField(max_length=50, null=True)
#     cvss = models.CharField(max_length=5, null=True)
#     cvss_time = models.DateTimeField(null=True)
#     cvss_vector = models.CharField(max_length=250, null=True)
#     cwe = models.CharField(max_length=10, null=True)
#     access = JSONField(default=access_default_dict)
#     impact = JSONField(default=impact_default_dict)
#     vulnerable_products = ArrayField(
#         models.CharField(max_length=10, blank=True), null=True)
#
#     is_exploitable = models.BooleanField(default=False)
#     exploit_ref = JSONField(default=dict, null=True)
#     exploit_info = JSONField(default=exploit_info_default_dict, null=True)
#
#     is_confirmed = models.BooleanField(default=False)
#     confirm_ref = ArrayField(
#         models.CharField(max_length=500, blank=True), null=True)
#     # exploit_availability = models.CharField(
#     #     max_length=20, choices=EXPLOIT_AVAILABILITY, default='unknown')
#     raw = JSONField(default=dict)
#
#     created_at = models.DateTimeField(default=timezone.now, null=True)
#     updated_at = models.DateTimeField(default=timezone.now, null=True)
#     history = HistoricalRecords()
#
#     class Meta:
#         db_table = "vuln_metadata"
#
#     def __unicode__(self):
#         return self.cve_id
#
#     def __str__(self):
#         return self.cve_id
#
#     def save(self, *args, **kwargs):
#         # Todo
#         if not self.created_at:
#             self.created_at = timezone.now()
#         self.updated_at = timezone.now()
#         return super(VulnMetadata, self).save(*args, **kwargs)


class ExploitMetadata(models.Model):
    vuln = models.ForeignKey(Vuln, on_delete=models.CASCADE)
    links = ArrayField(
        models.CharField(max_length=1500, blank=True), null=True)
    notes = models.TextField(default="")
    trust_level = models.CharField(
        max_length=20, choices=TRUST_LEVELS, default='unknown')
    tlp_level = models.CharField(
        max_length=20, choices=TLP_LEVELS, default='red')
    source = models.CharField(max_length=250, null=True)
    availability = models.CharField(
        max_length=20, choices=EXPLOIT_AVAILABILITY, default='unknown')
    type = models.CharField(
        max_length=20, choices=EXPLOIT_TYPES, default='unknown')
    maturity = models.CharField(
        max_length=20, choices=EXPLOIT_MATURITY_LEVELS, default='unknown')

    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "exploits_metadata"

    def __unicode__(self):
        return "VULN:{}/EXPLOIT:{}".format(self.vuln.id, self.id)

    def __str__(self):
        return "VULN:{}/EXPLOIT:{}".format(self.vuln.id, self.id)

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(ExploitMetadata, self).save(*args, **kwargs)


class ThreatMetadata(models.Model):
    vuln = models.ForeignKey(Vuln, on_delete=models.CASCADE)
    links = ArrayField(
        models.CharField(max_length=1500, blank=True), null=True)
    notes = models.TextField(default="")
    trust_level = models.CharField(
        max_length=20, choices=TRUST_LEVELS, default='unknown')
    tlp_level = models.CharField(
        max_length=20, choices=TLP_LEVELS, default='red')
    source = models.CharField(max_length=250, null=True)
    is_in_the_wild = models.BooleanField(default=False)
    is_in_the_news = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "threats_metadata"

    def __unicode__(self):
        return "VULN:{}/THREAT:{}".format(self.vuln.id, self.id)

    def __str__(self):
        return "VULN:{}/THREAT:{}".format(self.vuln.id, self.id)

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(ThreatMetadata, self).save(*args, **kwargs)
