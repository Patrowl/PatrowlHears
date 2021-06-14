from django.contrib import admin
from .models import DataSync, DataSyncJob, DataFeedImport

admin.site.register(DataSyncJob)
admin.site.register(DataSync)
admin.site.register(DataFeedImport)
