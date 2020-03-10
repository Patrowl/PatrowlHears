from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from simple_history.models import HistoricalRecords
from vulns.models import Vuln
from datetime import datetime
import logging
logger = logging.getLogger('django')


################
# Vulnerability: a bug, flaw, weakness, or exposure of an application, system,
#   device, or service that could lead to a failure of confidentiality,
#   integrity, or availability.
# Threat: the likelihood or frequency of a harmful event occurring.
# Risk: the relative impact that an exploited vulnerability would have to a
#   user's environment.
################

VPR_METRICS = {
    'vulnerability': {
        'max_score': 5,
        'cvss2_base_score': {   # 70% --> max_cvss=3,5
            'default': 2.5,
        },
        'cvss2': {
            'access': {
                'complexity': {
                    'default': 0.35,
                    'low': 0.71,
                    'medium': 0.61,
                    'high': 0.35
                },
                'authentication': {
                    'default': 0.704,
                    'none': 0.704,
                    'single': 0.56,
                    'multiple': 0.45
                },
                'vector': {
                    'default': 0.395,
                    'local': 0.395,
                    'adjacent': 0.646,
                    'network': 1
                }
            },
            'impact': {
                'confidentiality': {
                    'default': 0,
                    'none': 0,
                    'partial': 0.275,
                    'complete': 0.660,
                    'high': 0.660
                },
                'integrity': {
                    'default': 0,
                    'none': 0,
                    'partial': 0.275,
                    'complete': 0.660,
                    'high': 0.660
                },
                'availability': {
                    'default': 0,
                    'none': 0,
                    'partial': 0.275,
                    'complete': 0.660,
                    'high': 0.660
                }
            }
        },
        'confirmation': {
            'default': 0,
            'is_confirmed': 0.25
        },
        'remediation': {
            'default': 0,
            'unknown': 0,
            'unavailable': -0.75,
            'workaround': 0.5,
            'temporary': 0.66,
            'official': 0.75,
        },
        'age': {    # Less than N days
            'default': 0.33,
            'caps': {
                '15': 0.25,
                '45': 0.33,
                '10000000': 0.5
            }
        },
    },
    'threat': {
        'max_score': 5,
        'exploit_availability': {
            'default': 1,
            'unknown': 1,
            'private': 2,
            'public': 3
        },
        'exploit_maturity': {
            'default': 0,
            'unknown': 0,
            'unproven': 0.25,
            'poc': 0.75,
            'functional': 1
        },
        'exploit_trust': {
            'default': 0,
            'unknown': 0,
            'low': 0.1,
            'medium': 0.25,
            'high': 0.5,
            'trusted': 0.5
        },
        'exploit_age': {    # Less than N days
            'default': 0.33,
            'caps': {
                '15': 0.25,
                '45': 0.33,
                '10000000': 0.5
            }
        },
        'threat_intensity': {
            'default': 0,
            'is_in_the_news': 0.66,
            'is_in_the_wild': 0.66,
            # 'is_in_the_news': 0.75,
            # 'is_in_the_wild': 0.75
        },
    },
    'asset': {
        'max_score': 4,
        'criticality': {
            'default': 0.3,
            'low': 0.1,
            'medium': 0.3,
            'high': 1
        },
        'exposure': {
            'default': 1,
            'restricted': 0.5,
            'internal': 1,
            'external': 2
        },
        'distribution': {
            'default': 0.5,
            'low': 0.2,
            'medium': 0.5,
            'high': 1
        }
    }
}

VPR_DEFAULT_SCORES = {
    'vuln': 0,
    'threat': 0,
    'asset': 1.7
}


def get_default_scores():
    return dict(vuln=0, threat=0, asset=0)

# class VPRatingPolicy(models.Model):
#     name = models.CharField(max_length=255, default="")
#     comments = models.TextField(default="")
#     rules = JSONField(default=dict)
#     created_at = models.DateTimeField(default=timezone.now, null=True)
#     updated_at = models.DateTimeField(default=timezone.now, null=True)
#     history = HistoricalRecords()
#
#     class Meta:
#         db_table = "vpratings_policies"
#
#     def __unicode__(self):
#         return self.name
#
#     def __str__(self):
#         return self.name
#
#     def save(self, *args, **kwargs):
#         if not self.created_at:
#             self.created_at = timezone.now()
#         self.updated_at = timezone.now()
#         return super(VPRatingPolicy, self).save(*args, **kwargs)


class VPRating(models.Model):
    vector = models.CharField(max_length=255, default="")
    score = models.IntegerField(default=0)
    score_details = JSONField(default=get_default_scores)
    cvssv2adj = models.FloatField(default=0.0)
    data = JSONField(default=dict)
    vuln = models.ForeignKey(Vuln, on_delete=models.CASCADE)
    # policy = models.ForeignKey(VPRatingPolicy, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "vpratings"

    def __unicode__(self):
        return "PH-{}:{}".format(self.vuln.id, self.score)

    def __str__(self):
        return "PH-{}:{}".format(self.vuln.id, self.score)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(VPRating, self).save(*args, **kwargs)

    def calc_cvssv2adj(self):
        # Todo
        # print('calc_cvssv2adj:', self.score, self.vector, self.vuln.cvss2)
        return self.cvssv2adj

    def calc_score(self):
        if not self.data:   # Empty data
            self.score = 0
            self.score_details = VPR_DEFAULT_SCORES
        else:
            # self.score = int(self._calc_vpr_vuln() * self._calc_vpr_threat() * self._calc_vpr_asset())
            vpr_vuln = self._calc_vpr_vuln()
            vpr_threat = self._calc_vpr_threat()
            vpr_asset = self._calc_vpr_asset()
            self.score = int(
                vpr_vuln * 12 +
                vpr_threat * 4 +
                vpr_asset * 5)
            self.score_details = {
                'vuln': vpr_vuln,
                'threat': vpr_threat,
                'asset': vpr_asset
            }
        # print('calc_score:', self.score, self.score_details)
        return self.score

    def _calc_vpr_vuln(self):
        # print("_calc_vpr_vuln()", self.data['vulnerability'])
        vpr_vuln_score = 0.0

        # CVSSv2 Base Score (Impact + Exploitability)
        if 'cvss' in self.data['vulnerability'].keys():
            vpr_vuln_score += (self.data['vulnerability']['cvss'] * 70/100/2)
        else:
            vpr_vuln_score += VPR_METRICS['vulnerability']['cvss']['default']

        # Confirmation
        if 'is_confirmed' in self.data['vulnerability'].keys() and self.data['vulnerability']['is_confirmed'] is True:
            vpr_vuln_score += VPR_METRICS['vulnerability']['confirmation']['is_confirmed']
        else:
            vpr_vuln_score += VPR_METRICS['vulnerability']['confirmation']['default']

        # Remediation
        if 'remediation' in self.data['vulnerability'].keys() and self.data['vulnerability']['remediation'] in VPR_METRICS['vulnerability']['remediation'].keys():
            vpr_vuln_score += VPR_METRICS['vulnerability']['remediation'][self.data['vulnerability']['remediation']]
        else:
            vpr_vuln_score += VPR_METRICS['vulnerability']['remediation']['default']

        # Age
        if 'published' in self.data['vulnerability'].keys():
            for c in VPR_METRICS['vulnerability']['age']['caps'].keys():
                pubdate = self.data['vulnerability']['published']
                delta = datetime.now() - pubdate
                if delta.days <= int(c):
                    vpr_vuln_score += VPR_METRICS['vulnerability']['age']['caps'][c]
                    break
        else:
            vpr_vuln_score += VPR_METRICS['vulnerability']['age']['default']

        # Cap maximum value
        if vpr_vuln_score > VPR_METRICS['vulnerability']['max_score']:
            vpr_vuln_score = VPR_METRICS['vulnerability']['max_score']

        # print("vpr_vuln_score:", vpr_vuln_score)
        return vpr_vuln_score

    def _calc_vpr_threat(self):
        # print("_calc_vpr_threat()", self.data['threat'])
        vpr_threat_score = 0

        # List exploits
        max_exploit_score = 0

        # Loop into exploits and get the top valuable metadata
        for exploit in self.vuln.exploitmetadata_set.all():
            exploit_score = 0

            # Availability
            exploit_score += VPR_METRICS['threat']['exploit_availability'][exploit.availability]

            # Maturity
            exploit_score += VPR_METRICS['threat']['exploit_maturity'][exploit.maturity]

            # Trust level
            exploit_score += VPR_METRICS['threat']['exploit_trust'][exploit.trust_level]

            # Exploit Age
            for c in VPR_METRICS['threat']['exploit_age']['caps'].keys():
                if exploit.published is not None:
                    delta = datetime.now() - exploit.published
                    if delta.days <= int(c):
                        exploit_score += VPR_METRICS['threat']['exploit_age']['caps'][c]
                        break
            else:
                exploit_score += VPR_METRICS['threat']['exploit_age']['default']

            if exploit_score > max_exploit_score:
                max_exploit_score = exploit_score

        vpr_threat_score += max_exploit_score

        # Threat Intensity
        if self.vuln.is_in_the_news:
            vpr_threat_score += VPR_METRICS['threat']['threat_intensity']['is_in_the_news']
        if self.vuln.is_in_the_wild:
            vpr_threat_score += VPR_METRICS['threat']['threat_intensity']['is_in_the_wild']

        # Cap maximum value
        if vpr_threat_score > VPR_METRICS['threat']['max_score']:
            vpr_threat_score = VPR_METRICS['threat']['max_score']

        # print("vpr_threat_score:", vpr_threat_score)
        return vpr_threat_score

    def _calc_vpr_asset(self):
        # print("_calc_vpr_exploit()", self.data['asset'])
        vpr_asset_score = 0

        # Exposure
        if 'exposure' in self.data['asset'].keys() and self.data['asset']['exposure'] in VPR_METRICS['asset']['exposure'].keys():
            vpr_asset_score += VPR_METRICS['asset']['exposure'][self.data['asset']['exposure']]
        else:
            vpr_asset_score += VPR_METRICS['asset']['exposure']['default']

        # Criticality
        if 'criticality' in self.data['asset'].keys() and self.data['asset']['criticality'] in VPR_METRICS['asset']['criticality'].keys():
            vpr_asset_score += VPR_METRICS['asset']['criticality'][self.data['asset']['criticality']]
        else:
            vpr_asset_score += VPR_METRICS['asset']['criticality']['default']

        # Distribution
        if 'distribution' in self.data['asset'].keys() and self.data['asset']['distribution'] in VPR_METRICS['asset']['distribution'].keys():
            vpr_asset_score += VPR_METRICS['asset']['distribution'][self.data['asset']['distribution']]
        else:
            vpr_asset_score += VPR_METRICS['asset']['distribution']['default']

        # Cap maximum value
        if vpr_asset_score > VPR_METRICS['asset']['max_score']:
            vpr_asset_score = VPR_METRICS['asset']['max_score']

        # print("vpr_asset_score:", vpr_asset_score)
        return vpr_asset_score
