from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Vuln, ExploitMetadata, ThreatMetadata

admin.site.register(Vuln, SimpleHistoryAdmin)
admin.site.register(ExploitMetadata, SimpleHistoryAdmin)
admin.site.register(ThreatMetadata, SimpleHistoryAdmin)
