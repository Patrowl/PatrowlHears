from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import MonitoredAsset

admin.site.register(MonitoredAsset, SimpleHistoryAdmin)
