import mongoengine as me
import datetime


class MonitoredAsset(me.Document):
    name = me.StringField(required=True, unique=True)
    type = me.StringField(choices=('CVE', 'Vendor', 'Product', 'People', 'Keyword'), required=True)
    created_at = me.DateTimeField(default=datetime.datetime.now)
    updated_at = me.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    # def clean(self):
    #     pass

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        return super(MonitoredAsset, self).save(*args, **kwargs)


class VPRating(me.Document):
    name = me.StringField(required=True, unique=True)
    monitored_asset = me.ReferenceField(MonitoredAsset, required=True)
    created_at = me.DateTimeField(default=datetime.datetime.now)
    updated_at = me.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    # def clean(self):
    #     pass

    def save(self, *args, **kwargs):
        # Todo
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        return super(MonitoredAsset, self).save(*args, **kwargs)
