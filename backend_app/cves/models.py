from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
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


class Vendor(models.Model):
    name = models.TextField(max_length=250, default="-", unique=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "kb_vendor"
        indexes = [
            models.Index(fields=['name'])
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def is_monitored(self, org):
        return self in org.org_monitoring_list.vendors.all()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, touch=True, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(Vendor, self).save(*args, **kwargs)


class Product(models.Model):
    name = models.TextField(max_length=250, default="-")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    versions = ArrayField(
        models.CharField(max_length=250, blank=True), null=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "kb_product"
        unique_together = (('name', 'vendor'),)
        indexes = [
            models.Index(fields=['name'])
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'versions': self.versions,
            'vendor_id': self.vendor.id,
            'vendor': self.vendor.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def is_monitored(self, org):
        return self in org.org_monitoring_list.products.all()

    def save(self, touch=True, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(Product, self).save(*args, **kwargs)


class ProductVersion(models.Model):
    version = models.TextField(max_length=250, default="*")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vector = models.CharField(max_length=250, default="", null=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "kb_product_version"
        unique_together = (('version', 'vector', 'product'),)

    def __unicode__(self):
        return "{} - {}".format(self.product.name, self.version)

    def __str__(self):
        return "{} - {}".format(self.product.name, self.version)

    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'product_id': self.product.id,
            'product': self.product.name,
            'vendor_id': self.product.vendor.id,
            'vendor': self.product.vendor.name,
            'vector': self.vector,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, touch=True, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(ProductVersion, self).save(*args, **kwargs)


class PackageType(models.Model):
    name = models.TextField(max_length=250, default="others")
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    # history = HistoricalRecords()

    class Meta:
        db_table = "kb_package_type"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    #
    # def is_monitored(self, org):
    #     return self in org.org_monitoring_list.products.all()

    def save(self, touch=True, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(PackageType, self).save(*args, **kwargs)


class Package(models.Model):
    name = models.TextField(max_length=250, default="-")
    type = models.ForeignKey(PackageType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    # history = HistoricalRecords()

    class Meta:
        db_table = "kb_package"
        unique_together = (('name', 'type'),)

    def __unicode__(self):
        return "{}/{}".format(self.type.name, self.name)

    def __str__(self):
        return "{}/{}".format(self.type.name, self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    #
    # def is_monitored(self, org):
    #     return self in org.org_monitoring_list.products.all()

    def save(self, touch=True, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(Package, self).save(*args, **kwargs)


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

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'vendor_id': self.product.vendor.id,
            'vendor': self.product.vendor.name,
            'product_id': self.product.id,
            'product': self.product.name,
            'vector': self.vector,
            'vulnerable_products': self.vulnerable_products,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, touch=True, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(CPE, self).save(*args, **kwargs)


class CWE(models.Model):
    cwe_id = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=250, null=True)
    description = models.TextField(default="")
    refs = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        db_table = "kb_cwe"

    def __unicode__(self):
        return self.cwe_id

    def __str__(self):
        return self.cwe_id

    def to_dict(self):
        return {
            'id': self.id,
            'cwe_id': self.cwe_id,
            'name': self.name,
            'refs': self.refs,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, touch=True, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(CWE, self).save(*args, **kwargs)


class Bulletin(models.Model):
    publicid = models.CharField(max_length=250, default="", null=True)
    vendor = models.CharField(max_length=250, default="", null=True)
    title = models.CharField(max_length=250, default="", null=True)
    severity = models.CharField(max_length=250, default="", null=True)
    impact = models.CharField(max_length=250, default="", null=True)
    published = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    # raw = models.JSONField(default=dict, blank=True, null=True)
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

    def to_dict(self):
        return {
            'id': self.id,
            'publicid': self.publicid,
            'vendor': self.vendor,
            'title': self.title,
            'severity': self.severity,
            'impact': self.impact,
            'published': self.published,
            'modified': self.modified,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, touch=True, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(Bulletin, self).save(*args, **kwargs)


class CVE(models.Model):
    cve_id = models.CharField(max_length=20, null=True, unique=True)
    summary = models.TextField(default="", blank=True)
    products = models.ManyToManyField(Product, related_name='cves')
    productversions = models.ManyToManyField(ProductVersion, related_name='cves')
    published = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    assigner = models.CharField(max_length=50, null=True)
    cvss = models.FloatField(default=0.0, null=True)
    cvss_time = models.DateTimeField(null=True)
    cvss_vector = models.CharField(max_length=250, blank=True, null=True)
    cvss_version = models.CharField(max_length=5, blank=True, null=True)
    cvss_metrics = models.JSONField(default=dict)
    cvss3 = models.FloatField(default=0.0, null=True)
    cvss3_vector = models.CharField(max_length=250, blank=True, null=True)
    cvss3_version = models.CharField(max_length=5, blank=True, null=True)
    cvss3_metrics = models.JSONField(default=dict)
    cwe = models.ForeignKey(CWE, on_delete=models.CASCADE, blank=True, null=True)
    access = models.JSONField(default=access_default_dict)
    impact = models.JSONField(default=impact_default_dict)
    vulnerable_products = ArrayField(
        models.CharField(max_length=250, blank=True), blank=True, null=True)
    bulletins = models.ManyToManyField(Bulletin, blank=True)
    references = models.JSONField(default=dict)
    monitored = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    # history = HistoricalRecords()

    class Meta:
        db_table = "kb_cve"

    def __unicode__(self):
        return self.cve_id

    def __str__(self):
        return self.cve_id

    def to_dict(self):
        cwe_id = ""
        if self.cwe:
            cwe_id = self.cwe.id
        return {
            'id': self.id,
            'cve_id': self.cve_id,
            'summary': self.summary,
            'products': [p.id for p in self.products.all()],
            'productversions': [p.id for p in self.productversions.all()],
            'published': self.published,
            'modified': self.modified,
            'assigner': self.assigner,
            'cvss': self.cvss,
            'cvss_time': self.cvss_time,
            'cvss_vector': self.cvss_vector,
            'cvss_version': self.cvss3_version,
            'cvss_metrics': self.cvss_metrics,
            'cvss3': self.cvss3,
            'cvss3_vector': self.cvss3_vector,
            'cvss3_version': self.cvss3_version,
            'cvss3_metrics': self.cvss3_metrics,
            'cwe': cwe_id,
            'access': self.access,
            'impact': self.impact,
            'vulnerable_products': self.vulnerable_products,
            'bulletins': [b.id for b in self.bulletins.all()],
            'references': self.references,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, touch=True, *args, **kwargs):
        if float(self.cvss) > 10:
            self.cvss = 10
        if float(self.cvss3) > 10:
            self.cvss3 = 10
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        return super(CVE, self).save(*args, **kwargs)
