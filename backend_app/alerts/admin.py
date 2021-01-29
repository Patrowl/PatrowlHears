from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import AlertingRule, AlertingTemplate

admin.site.register(AlertingRule, SimpleHistoryAdmin)
admin.site.register(AlertingTemplate, SimpleHistoryAdmin)
