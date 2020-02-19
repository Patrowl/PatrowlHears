from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save
from django.dispatch import receiver
from alerts.models import AlertingRule
from cves.models import CVE, CWE
from common.utils.constants import (
    EXPLOIT_AVAILABILITY, EXPLOIT_TYPES, EXPLOIT_MATURITY_LEVELS,
    TRUST_LEVELS, TLP_LEVELS)
from common.utils import _json_serial
import json


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


class Vuln(models.Model):
    cve_id = models.ForeignKey(CVE, on_delete=models.CASCADE, null=True)
    summary = models.TextField(default="")
    published = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    assigner = models.CharField(max_length=50, null=True)
    cwe = models.ForeignKey(CWE, on_delete=models.CASCADE, null=True)
    vulnerable_products = ArrayField(
        models.CharField(max_length=250, blank=True), null=True)
    access = JSONField(default=access_default_dict)
    impact = JSONField(default=impact_default_dict)

    cvss = models.FloatField(default=0.0, null=True)
    cvss_time = models.DateTimeField(null=True)
    cvss_vector = models.CharField(max_length=250, null=True)
    access = JSONField(default=access_default_dict)
    impact = JSONField(default=impact_default_dict)

    score = models.IntegerField(default=0, null=True)

    is_exploitable = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_in_the_news = models.BooleanField(default=False)
    is_in_the_wild = models.BooleanField(default=False)
    reflinks = JSONField(default=dict)
    reflinkids = JSONField(default=dict)

    monitored = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        db_table = "vulns"

    def __init__(self, *args, **kwargs):
        super(Vuln, self).__init__(*args, **kwargs)
        self.__important_fields = [
            'cve_id', 'summary', 'published', 'modified', 'assigner',
            # 'vulnerable_products',
            'cvss', 'cvss_time', 'cvss_vector',
            'access', 'impact',
            'is_exploitable', 'is_confirmed',
            'is_in_the_news', 'is_in_the_wild',
            'score',
            'monitored']
        for field in self.__important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def __unicode__(self):
        return "PH-{}".format(self.id)

    def __str__(self):
        return "PH-{}".format(self.id)

    def to_dict(self):
        # from vpratings.utils import _calc_vprating
        j = {
            'id': self.id,
            'cve_id': self.cve_id.cve_id,
            'summary': self.summary,
            'published': self.published,
            'modified': self.modified,
            'assigner': self.assigner,
            # 'cwe': self.cwe.cwe_id,
            'cwe': getattr(self.cwe, 'cwe_id', None),
            'vulnerable_products': self.vulnerable_products,
            'cvss': self.cvss,
            'cvss_time': self.cvss_time,
            'cvss_vector': self.cvss_vector,
            'access': self.access,
            'impact': self.impact,
            'is_exploitable': self.is_exploitable,
            'is_confirmed': self.is_confirmed,
            'is_in_the_news': self.is_in_the_news,
            'is_in_the_wild': self.is_in_the_wild,
            # 'rating': _calc_vprating(self).score,
            'score': self.score,
            'reflinks': self.reflinks,
            'monitored': self.monitored,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'exploit_cnt': self.exploitmetadata_set.count(),
            # 'exploits': self.exploitmetadata_set,
            # 'threats': self.threatmetadata_set,
        }
        return j

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

    def update_score(self):
        from vpratings.utils import _calc_vprating
        self.score = _calc_vprating(self).score

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        self.update_score()
        return super(Vuln, self).save(*args, **kwargs)


class ExploitMetadata(models.Model):
    vuln = models.ForeignKey(Vuln, on_delete=models.CASCADE)
    publicid = models.CharField(max_length=250, default='n/a')
    link = models.CharField(max_length=1500, blank=True, default="")
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
    raw = JSONField(default=dict)
    published = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    hash = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    class Meta:
        db_table = "exploits_metadata"

    def __unicode__(self):
        return "VULN:{}/EXPLOIT:{}".format(self.vuln.id, self.id)

    def __str__(self):
        return "VULN:{}/EXPLOIT:{}".format(self.vuln.id, self.id)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        if self.vuln.is_exploitable is False:
            self.vuln.is_exploitable = True
            # self.vuln.save()
        self.vuln.update_score()
        self.vuln.save()
        return super(ExploitMetadata, self).save(*args, **kwargs)


class ThreatMetadata(models.Model):
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
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

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
        self.vuln.update_score()
        self.vuln.save()
        return super(ThreatMetadata, self).save(*args, **kwargs)


@receiver(post_save, sender=Vuln)
def alerts_vulnerability_save(sender, **kwargs):
    if kwargs['instance']._state.adding:
        # Check alerting rules
        for alert in AlertingRule.objects.filter(target='add_vuln', enabled=True):
            vuln_conditions = alert.conditions.get('vuln', None)
            vuln_conditions.update({'id': kwargs['instance'].id})
            if Vuln.objects.filter(**vuln_conditions).first():
                alert.notify(short=alert.title, long=kwargs['instance'].to_dict(), template='vuln')
    else:
        changes = kwargs['instance'].get_changes()
        if len(changes) > 0:
            # Check alerting rules
            for alert in AlertingRule.objects.filter(target='update_vuln', enabled=True):
                # Check if at least one changed field has to be checked
                if any(i in changes for i in alert.check_fields):
                    vuln_conditions = alert.conditions.get('vuln', None)
                    vuln_conditions.update({'id': kwargs['instance'].id})
                    if Vuln.objects.filter(**vuln_conditions).first():
                        alert.notify(short=alert.title, long=kwargs['instance'].to_dict(), template='vuln')

#
# @receiver(post_save, sender=ExploitMetadata)
# def alerts_exploit_save(sender, **kwargs):
#     if kwargs['instance']._state.adding:
#         # Check alerting rules
#         for alert in AlertingRule.objects.filter(target='add_exploit', enabled=True):
#             vuln_conditions = alert.conditions.get('vuln', None)
#             exploit_conditions = alert.conditions.get('exploit', None)
#             exploit_conditions.update({'id': kwargs['instance'].id})
#             if Vuln.objects.filter(**vuln_conditions).first() and ExploitMetadata.objects.filter(**exploit_conditions).first():
#                 alert.notify(short=alert.title, long=kwargs['instance'])
#     else:
#         changes = kwargs['instance'].get_changes()
#         if len(changes) > 0:
#             # Check alerting rules
#             for alert in AlertingRule.objects.filter(target='update_exploit', enabled=True):
#                 # Check if at least one changed field has to be checked
#                 if any(i in changes for i in alert.check_fields):
#                     vuln_conditions = alert.conditions.get('vuln', None)
#                     vuln_conditions.update({'id': kwargs['instance'].id})
#                     if Vuln.objects.filter(**vuln_conditions).first():
#                         alert.notify(short=alert.title, long=kwargs['instance'])
