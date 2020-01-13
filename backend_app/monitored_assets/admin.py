from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import MonitoredAsset, AssetMetadata

admin.site.register(MonitoredAsset, SimpleHistoryAdmin)
admin.site.register(AssetMetadata, SimpleHistoryAdmin)
