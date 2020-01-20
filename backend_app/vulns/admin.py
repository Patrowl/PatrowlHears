from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import VulnMetadata, ExploitMetadata

admin.site.register(VulnMetadata, SimpleHistoryAdmin)
admin.site.register(ExploitMetadata, SimpleHistoryAdmin)
