from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import VulnMetadata

admin.site.register(VulnMetadata, SimpleHistoryAdmin)
