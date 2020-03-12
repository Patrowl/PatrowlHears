from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField
from simple_history.models import HistoricalRecords
# from monitored_assets.models import MonitoredProduct


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


class Vendor(models.Model):
    name = models.TextField(max_length=250, default="-")
    monitored = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "kb_vendor"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Vendor, self).save(*args, **kwargs)


class Product(models.Model):
    name = models.TextField(max_length=250, default="-")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    monitored = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "kb_product"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Product, self).save(*args, **kwargs)


class ProductVersion(models.Model):
    version = models.TextField(max_length=250, default="*")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vector = models.CharField(max_length=250, default="", null=True)
    monitored = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "kb_product_version"

    def __unicode__(self):
        return "{} - {}".format(self.product.name, self.version)

    def __str__(self):
        return "{} - {}".format(self.product.name, self.version)

    def to_dict(self):
        return {
            'version': self.version,
            'product': self.product.name,
            'vendor': self.product.vendor.name,
            'vector': self.vector,
            'monitored': self.monitored
        }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(ProductVersion, self).save(*args, **kwargs)


class CPE(models.Model):
    title = models.TextField(default="")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    vector = models.CharField(max_length=250, default="", null=True)
    vulnerable_products = ArrayField(
        models.CharField(max_length=250, blank=True), null=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

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
    modified = models.DateTimeField(blank=True, null=True)
    # raw = JSONField(default=dict, blank=True, null=True)
    monitored = models.BooleanField(default=False)
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
    products = models.ManyToManyField(Product, related_name='cves')
    productversions = models.ManyToManyField(ProductVersion, related_name='cves')
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
        models.CharField(max_length=250, blank=True), null=True)
    bulletins = models.ManyToManyField(Bulletin, blank=True)
    references = JSONField(default=dict)
    monitored = models.BooleanField(default=False)
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
