from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save
from django.dispatch import receiver
from organizations.models import Organization
from alerts.models import AlertingRule
from alerts.tasks import slack_alert_vuln_task
from cves.models import CVE, CWE, Product, ProductVersion, Package
from common.utils.constants import (
    EXPLOIT_AVAILABILITY, EXPLOIT_TYPES, EXPLOIT_MATURITY_LEVELS,
    TRUST_LEVELS, TLP_LEVELS,
    EXPLOIT_RELEVANCY_RATES
)
from common.utils import _json_serial
from cpe import CPE as _CPE
import json
import math


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


class VulnBase(models.Model):
    # uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    uuid = models.UUIDField(null=True, editable=True, unique=False, blank=True)
    feedid = models.CharField(max_length=250, null=True, blank=True, default="")
    cve = models.ForeignKey(CVE, on_delete=models.CASCADE, null=True, blank=True)
    cveid = models.CharField(max_length=50, null=True, blank=True, default="")
    summary = models.TextField(default="", blank=True)
    published = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    assigner = models.CharField(max_length=128, null=True)
    cwe = models.ForeignKey(CWE, on_delete=models.CASCADE, blank=True, null=True)

    packages = models.ManyToManyField(Package, related_name='vulns')
    vulnerable_packages_versions = JSONField(default=dict)
    products = models.ManyToManyField(Product, related_name='vulns')
    productversions = models.ManyToManyField(ProductVersion, related_name='vulns')
    vulnerable_products = ArrayField(
        models.CharField(max_length=250, blank=True), blank=True, null=True)  # CPE list
    vulnerable_product_versions = JSONField(default=dict)

    cvss = models.FloatField(default=0.0, null=True)  # CVSSv2
    cvss_time = models.DateTimeField(null=True)
    cvss_version = models.CharField(max_length=5, blank=True, null=True)
    cvss_vector = models.CharField(max_length=250, blank=True, null=True)
    cvss_metrics = JSONField(default=dict)
    access = JSONField(default=access_default_dict)
    impact = JSONField(default=impact_default_dict)
    cvss3 = models.FloatField(default=0.0, null=True)
    cvss3_vector = models.CharField(max_length=250, blank=True, null=True)
    cvss3_version = models.CharField(max_length=5, blank=True, null=True)
    cvss3_metrics = JSONField(default=dict)

    score = models.IntegerField(default=0)

    is_exploitable = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_in_the_news = models.BooleanField(default=False)
    is_in_the_wild = models.BooleanField(default=False)
    reflinks = JSONField(default=dict, blank=True)
    reflinkids = JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    # history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        # db_table = "vulns"
        abstract = True
        # indexes = [
        #     models.Index(fields=['cveid']),
        #     models.Index(fields=['feedid']),
        # ]

    def __init__(self, *args, **kwargs):
        super(VulnBase, self).__init__(*args, **kwargs)
        self.__important_fields = [
            'uuid',
            'cve_id', 'summary', 'published', 'modified', 'assigner',
            'vulnerable_packages_versions',
            'cvss', 'cvss_time', 'cvss_vector', 'cvss_version', 'cvss_metrics',
            'cvss3', 'cvss3_vector', 'cvss3_version', 'cvss3_metrics',
            'access', 'impact',
            'is_exploitable', 'is_confirmed',
            'is_in_the_news', 'is_in_the_wild',
            'score'
        ]
        for field in self.__important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def __unicode__(self):
        return "PH-{}".format(self.id)

    def __str__(self):
        return "PH-{}".format(self.id)

    def to_dict(self):
        cve_id = ""
        if self.cve:
            cve_id = self.cve.id
        cwe_id = ""
        cwe_name = ""
        if self.cwe:
            cwe_id = self.cwe.id
            cwe_name = self.cwe.name
        return {
            'id': self.id,
            'uuid': self.uuid,
            'cveid': self.cveid,
            'cve': cve_id,
            'summary': self.summary,
            'published': self.published,
            'modified': self.modified,
            'assigner': self.assigner,
            'cwe': cwe_id,
            'cwe_name': cwe_name,
            'vulnerable_products': self.vulnerable_products,
            'packages': [p.id for p in self.packages.all()],
            'vulnerable_packages_versions': self.vulnerable_packages_versions,
            'products': [p.id for p in self.products.all()],
            'productversions': [p.id for p in self.productversions.all()],
            'cvss': self.cvss,
            'cvss_time': self.cvss_time,
            'cvss_vector': self.cvss_vector,
            'cvss_version': self.cvss3_version,
            'cvss_metrics': self.cvss_metrics,
            'cvss3': self.cvss3,
            'cvss3_vector': self.cvss3_vector,
            'cvss3_version': self.cvss3_version,
            'cvss3_metrics': self.cvss3_metrics,
            'access': self.access,
            'impact': self.impact,
            'is_exploitable': self.is_exploitable,
            'is_confirmed': self.is_confirmed,
            'is_in_the_news': self.is_in_the_news,
            'is_in_the_wild': self.is_in_the_wild,
            'score': self.score,
            'reflinks': self.reflinks,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'exploit_cnt': self.exploitmetadata_set.count(),
            'exploit_count': self.exploitmetadata_set.count(),
        }

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, default=_json_serial)
    #
    # def has_changed(self):
    #     for field in self.__important_fields:
    #         orig = '__original_%s' % field
    #         if getattr(self, orig) != getattr(self, field):
    #             return True
    #     return False

    def get_changes(self):
        changes = []
        for field in self.__important_fields:
            orig = '__original_%s' % field
            if getattr(self, orig) != getattr(self, field):
                changes.append(field)
        return changes

    def update_score(self, org=None):
        from vpratings.utils import _calc_vprating
        # print("update_score:", org)
        self.score = _calc_vprating(self, org=org).score
        return self.score

    def update_product_versions(self):
        data = {}
        all_versions = []
        for vp in self.vulnerable_products:
            try:
                c = _CPE(vp)
                v = c.get_vendor()[0]
                p = c.get_product()[0]
                s = c.get_version()[0]
                all_versions.append(s)
                if v not in data.keys():
                    data.update({v: {}})
                if p not in data[v].keys():
                    data[v].update({p: []})
                if s not in data[v][p]:
                    data[v][p].append(s)
            except Exception:
                pass
        data.update({
            "all": list(set(all_versions))
        })
        self.vulnerable_product_versions = data
        return self.vulnerable_product_versions

    def save(self, touch=True, *args, **kwargs):
        if float(self.cvss) > 10:
            self.cvss = 10
        if float(self.cvss3) > 10:
            self.cvss3 = 10

        if not self.created_at:
            self.created_at = timezone.now()

        if 'org' in kwargs.keys():
            org = kwargs.pop('org')
            self.update_score(org=org)
        else:
            self.update_score()

        if len(self.get_changes()) > 0 and touch:
            self.updated_at = timezone.now()
        return super(VulnBase, self).save(*args, **kwargs)


class Vuln(VulnBase):
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        db_table = "vulns"

        indexes = [
            models.Index(fields=['cveid']),
            models.Index(fields=['feedid']),
        ]
#
#
# class OrgVulnChange(VulnBase):
#     organization = AutoOneToOneField(Organization, on_delete=models.CASCADE, related_name='org_vulns')
#     products = models.ManyToManyField(Product, related_name='org_vulns')
#     productversions = models.ManyToManyField(ProductVersion, related_name='org_vulns')
#     history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)
#
#     class Meta:
#         db_table = "org_vuln_changes"


class ExploitMetadataBase(models.Model):
    # uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    uuid = models.UUIDField(null=True, editable=True, unique=False)
    vuln = models.ForeignKey(Vuln, on_delete=models.CASCADE)
    publicid = models.CharField(max_length=250, default='n/a')
    link = models.CharField(max_length=1500, blank=True, default="")
    notes = models.TextField(default="")
    trust_level = models.CharField(
        max_length=20, choices=TRUST_LEVELS, default='unknown')
    tlp_level = models.CharField(
        max_length=20, choices=TLP_LEVELS, default='amber')
    source = models.CharField(max_length=250, null=True, default='patrowl')
    availability = models.CharField(
        max_length=20, choices=EXPLOIT_AVAILABILITY, default='unknown')
    type = models.CharField(
        max_length=20, choices=EXPLOIT_TYPES, default='unknown')
    maturity = models.CharField(
        max_length=20, choices=EXPLOIT_MATURITY_LEVELS, default='unknown')
    raw = JSONField(default=dict)
    published = models.DateTimeField(default=timezone.now, blank=True, null=True)
    modified = models.DateTimeField(default=timezone.now, blank=True, null=True)
    hash = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    # history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        abstract = True
    #     db_table = "exploits_metadata"

    def __unicode__(self):
        return "VULN:{}/EXPLOIT:{}".format(self.vuln.id, self.id)

    def __str__(self):
        return "VULN:{}/EXPLOIT:{}".format(self.vuln.id, self.id)

    def get_relevancy_level(self):
        # 1 to 5
        rl = 1
        rl += EXPLOIT_RELEVANCY_RATES['EXPLOIT_AVAILABILITY'][self.availability]
        rl += EXPLOIT_RELEVANCY_RATES['TRUST_LEVELS'][self.trust_level]
        rl += EXPLOIT_RELEVANCY_RATES['EXPLOIT_MATURITY_LEVELS'][self.maturity]

        return math.ceil(rl)

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'vuln_id': self.vuln.id,
            'vuln_uuid': self.vuln.uuid,
            'publicid': self.publicid,
            'link': self.link,
            'notes': self.notes,
            'trust_level': self.trust_level,
            'tlp_level': self.tlp_level,
            'source': self.source,
            'availability': self.availability,
            'type': self.type,
            'maturity': self.maturity,
            'published': self.published,
            'modified': self.modified,
            'relevancy_level': self.get_relevancy_level(),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, default=_json_serial)

    def save(self, touch=True, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()

        # If an exploit exists, the vuln is now exploitable
        if self.vuln.is_exploitable is False:
            self.vuln.is_exploitable = True
            # self.vuln.save()
        self.vuln.update_score()
        self.vuln.updated_at = timezone.now()
        self.vuln.save()
        return super(ExploitMetadataBase, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.vuln.updated_at = timezone.now()
        self.vuln.save()
        return super(ExploitMetadataBase, self).delete(*args, **kwargs)


class ExploitMetadata(ExploitMetadataBase):
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        db_table = "exploits_metadata"


class OrgExploitMetadata(ExploitMetadataBase):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='org_exploits')
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        db_table = "org_exploits_metadata"
        verbose_name = "Org exploit"
        verbose_name_plural = "Org exploits"


class ThreatMetadataBase(models.Model):
    # uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    uuid = models.UUIDField(null=True, editable=True, unique=False)
    vuln = models.ForeignKey(Vuln, on_delete=models.CASCADE)
    link = models.CharField(default="", max_length=1500, blank=True)
    notes = models.TextField(default="")
    trust_level = models.CharField(
        max_length=20, choices=TRUST_LEVELS, default='unknown')
    tlp_level = models.CharField(
        max_length=20, choices=TLP_LEVELS, default='red')
    source = models.CharField(max_length=250, null=True)
    is_in_the_wild = models.BooleanField(default=False)
    is_in_the_news = models.BooleanField(default=False)
    raw = JSONField(default=dict)
    published = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    # history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        # db_table = "threats_metadata"
        abstract = True

    def __unicode__(self):
        return "VULN:{}/THREAT:{}".format(self.vuln.id, self.id)

    def __str__(self):
        return "VULN:{}/THREAT:{}".format(self.vuln.id, self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'vuln_id': self.vuln.id,
            'vuln_uuid': self.vuln.uuid,
            'link': self.link,
            'notes': self.notes,
            'trust_level': self.trust_level,
            'tlp_level': self.tlp_level,
            'source': self.source,
            'is_in_the_wild': self.is_in_the_wild,
            'is_in_the_news': self.is_in_the_news,
            'published': self.published,
            'modified': self.modified,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, default=_json_serial)

    def save(self, touch=True, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        if touch:
            self.updated_at = timezone.now()
        self.vuln.update_score()
        self.vuln.updated_at = timezone.now()
        self.vuln.save()
        return super(ThreatMetadataBase, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.vuln.updated_at = timezone.now()
        self.vuln.save()
        return super(ThreatMetadataBase, self).delete(*args, **kwargs)


class ThreatMetadata(ThreatMetadataBase):
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        db_table = "threats_metadata"


class OrgThreatMetadata(ThreatMetadataBase):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='org_threats')
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        db_table = "org_threats_metadata"
        verbose_name = "Org threats new"
        verbose_name_plural = "Org threats news"


@receiver(post_save, sender=Vuln)
def alerts_vulnerability_save(sender, **kwargs):
    # New vulnerability
    if kwargs['instance']._state.adding:
        slack_alert_vuln_task.apply_async(
            args=[kwargs['instance'].id, "new"], queue='alerts', retry=False)
        # Check alerting rules
        # for alert in AlertingRule.objects.filter(target='add_vuln', enabled=True):
        #     vuln_conditions = alert.conditions.get('vuln', None)
        #     vuln_conditions.update({'id': kwargs['instance'].id})
        #     if Vuln.objects.filter(**vuln_conditions).first():
        #         alert.notify(short=alert.title, long=kwargs['instance'].to_dict(), template='vuln')
    else:
        # Vulnerability change
        changes = kwargs['instance'].get_changes()
        if len(changes) > 0:
            slack_alert_vuln_task.apply_async(
                args=[kwargs['instance'].id, "update"], queue='alerts', retry=False)
            # Check alerting rules
            for alert in AlertingRule.objects.filter(target='update_vuln', enabled=True):
                # Check if at least one changed field has to be checked
                if any(i in changes for i in alert.check_fields):
                    vuln_conditions = alert.conditions.get('vuln', None)
                    vuln_conditions.update({'id': kwargs['instance'].id})
                    if Vuln.objects.filter(**vuln_conditions).first():
                        alert.notify(short=alert.title, long=kwargs['instance'].to_dict(), template='vuln')
