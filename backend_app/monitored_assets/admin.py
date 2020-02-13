from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import MonitoredProduct
# from .models import MonitoredAsset

admin.site.register(MonitoredProduct, SimpleHistoryAdmin)
# admin.site.register(MonitoredAsset, SimpleHistoryAdmin)
