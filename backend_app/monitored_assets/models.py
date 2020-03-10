from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class MonitoredProduct(models.Model):
    vendor = models.CharField(max_length=255, default="")
    product = models.CharField(max_length=255, default="")
    version = models.CharField(max_length=255, default="", null=True, blank=True)
    monitored = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "monitored_products"

    def __unicode__(self):
        return "{} - {}".format(self.vendor, self.product)

    def __str__(self):
        return "{} - {}".format(self.vendor, self.product)

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(MonitoredProduct, self).save(*args, **kwargs)
