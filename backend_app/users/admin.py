from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
# from .models import User, OrgMonitoringList, OrgSettings
from .models import OrgMonitoringList, OrgSettings

# admin.site.register(User, UserAdmin)
admin.site.register(OrgMonitoringList)
admin.site.register(OrgSettings, SimpleHistoryAdmin)
