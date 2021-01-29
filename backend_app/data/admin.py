from django.contrib import admin
from .models import DataSync, DataSyncJob

admin.site.register(DataSyncJob)
admin.site.register(DataSync)
