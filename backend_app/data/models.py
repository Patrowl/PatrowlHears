from django.db import models
from django.utils import timezone
from common.utils.constants import DATASYNC_STATUS, DATASYNC_MODEL_NAMES
from common.utils.constants import DATA_FEEDS_IMPORT_TYPES


class DataFeedImport(models.Model):
    filename = models.TextField(default='')
    hash = models.TextField(default='')
    source = models.TextField(default='')
    type = models.CharField(max_length=20, choices=DATA_FEEDS_IMPORT_TYPES, default='vuln')
    object_id = models.BigIntegerField()
    has_error = models.BooleanField(default=False)
    comments = models.TextField(default='')
    imported_at = models.DateTimeField(default=timezone.now, null=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        db_table = "datafeedimport"
        indexes = [
            models.Index(fields=['hash']),
            models.Index(fields=['filename']),
        ]

    def __unicode__(self):
        return "[{}/{}/{}]".format(self.id, self.filename, self.hash)

    def __str__(self):
        return "[{}/{}/{}]".format(self.id, self.filename, self.hash)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'hash': self.hash,
            'source': self.source,
            'type': self.type,
            'object_id': self.object_id,
            'has_error': self.has_error,
            'comments': self.comments,
            'imported_at': self.imported_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(DataFeedImport, self).save(*args, **kwargs)


class DataSyncJob(models.Model):
    status = models.CharField(
        max_length=20, choices=DATASYNC_STATUS, default='started')
    progression = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        db_table = "datasyncjob"

    def __unicode__(self):
        return "[{}/{}/{}]".format(self.id, self.status, self.progression)

    def __str__(self):
        return "[{}/{}/{}]".format(self.id, self.status, self.progression)

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'progression': self.progression,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(DataSyncJob, self).save(*args, **kwargs)


class DataSync(models.Model):
    job = models.ForeignKey(DataSyncJob, on_delete=models.CASCADE, null=True)
    since_date = models.DateTimeField(null=True)
    to_date = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=20, choices=DATASYNC_STATUS, default='started')
    mdl_name = models.CharField(
        max_length=50, choices=DATASYNC_MODEL_NAMES, default='')
    from_id = models.IntegerField(blank=True, null=True)
    has_more_updates = models.BooleanField(default=True)
    comments = models.TextField(default="")
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        db_table = "datasync"

    def __unicode__(self):
        return "{}/{}/{}/{}/{}/{}/{}/{}".format(self.id, self.job, self.mdl_name, self.from_id, self.since_date, self.to_date, self.status, self.has_more_updates)

    def __str__(self):
        return "{}/{}/{}/{}/{}/{}/{}/{}".format(self.id, self.job, self.mdl_name, self.from_id, self.since_date, self.to_date, self.status, self.has_more_updates)

    def to_dict(self):
        return {
            'id': self.id,
            'job': self.job.to_dict(),
            'since_date': self.since_date,
            'since_date_epoch': self.since_date.strftime('%s'),
            'to_date': self.to_date,
            'to_date_epoch': self.to_date.strftime('%s'),
            'mdl_name': self.mdl_name,
            'from_id': self.from_id,
            'has_more_updates': self.has_more_updates,
            'status': self.status,
            'comments': self.comments,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(DataSync, self).save(*args, **kwargs)
