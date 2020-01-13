from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class MonitoredAsset(models.Model):
    ASSET_TYPES = (
        ('CVE', 'CVE'),
        ('Vendor', 'Vendor'),
        ('Product', 'Product'),
        ('People', 'People'),
        ('Keyword', 'Keyword')
    )
    MONITORING_STATUSES = (
        ('idle', 'Idle'),
        ('monitoring', 'Monitoring')
    )

    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=ASSET_TYPES)
    status = models.CharField(max_length=20, choices=MONITORING_STATUSES, default='monitoring')
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "monitored_assets"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    # def clean(self):
    #     pass

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(MonitoredAsset, self).save(*args, **kwargs)


class AssetMetadata(models.Model):
    asset = models.ForeignKey(MonitoredAsset, on_delete=models.CASCADE)
    version = models.CharField(max_length=255, unique=True)
    data = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "asset_metadata"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    # def clean(self):
    #     pass

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(MonitoredAsset, self).save(*args, **kwargs)
