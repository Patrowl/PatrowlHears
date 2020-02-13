from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

MONITORING_STATUSES = (
    ('idle', 'Idle'),
    ('monitoring', 'Monitoring')
)


class MonitoredProduct(models.Model):
    vendor = models.CharField(max_length=255, default="")
    product = models.CharField(max_length=255, default="")
    # type = models.CharField(max_length=20, choices=ASSET_TYPES)
    monitored = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "monitored_products"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(MonitoredProduct, self).save(*args, **kwargs)
