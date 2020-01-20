from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField
from simple_history.models import HistoricalRecords


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


class CPE(models.Model):
    title = models.TextField(default="")
    vendor = models.CharField(max_length=250, default="", null=True)
    product = models.CharField(max_length=250, default="", null=True)
    vector = models.CharField(max_length=250, default="", null=True)
    vulnerable_products = ArrayField(
        models.CharField(max_length=250, blank=True), null=True)

    class Meta:
        db_table = "kb_cpe"

    def __unicode__(self):
        return self.vector

    def __str__(self):
        return self.vector


class CWE(models.Model):
    cwe_id = models.CharField(max_length=20, null=True, unique=True)
    name = models.CharField(max_length=250, null=True)
    description = models.TextField(default="")

    class Meta:
        db_table = "kb_cwe"

    def __unicode__(self):
        return self.cwe_id

    def __str__(self):
        return self.cwe_id


class Bulletin(models.Model):
    publicid = models.CharField(max_length=250, default="", null=True)
    vendor = models.CharField(max_length=250, default="", null=True)
    title = models.CharField(max_length=250, default="", null=True)
    severity = models.CharField(max_length=250, default="", null=True)
    impact = models.CharField(max_length=250, default="", null=True)
    published = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "kb_bulletin"

    def __unicode__(self):
        return self.publicid

    def __str__(self):
        return self.publicid

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Bulletin, self).save(*args, **kwargs)


class CVE(models.Model):
    cve_id = models.CharField(max_length=20, null=True, unique=True)
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
    vulnerable_products = ArrayField(
        models.CharField(max_length=10, blank=True), null=True)
    bulletins = models.ManyToManyField(Bulletin, blank=True)
    references = JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "kb_cve"

    def __unicode__(self):
        return self.cve_id

    def __str__(self):
        return self.cve_id

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(CVE, self).save(*args, **kwargs)
