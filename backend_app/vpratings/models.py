from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from simple_history.models import HistoricalRecords
from vulns.models import VulnMetadata

#
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
    score = models.FloatField(default=0.0)
    data = JSONField(default=dict)
    vuln = models.ForeignKey(VulnMetadata, on_delete=models.CASCADE)
    # policy = models.ForeignKey(VPRatingPolicy, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "vpratings"

    def __unicode__(self):
        return "{}:{}".format(self.vuln.cve_id, self.score)

    def __str__(self):
        return "{}:{}".format(self.vuln.cve_id, self.score)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(VPRating, self).save(*args, **kwargs)

    def calc(self):
        # Uodate vector
        print('calc', self.score, self.vector)
        return True
