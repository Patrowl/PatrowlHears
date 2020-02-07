from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Vuln, ExploitMetadata, ThreatMetadata


class VulnAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('cve_id', 'cwe',)


class ExploitAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('vuln',)


class ThreatAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('vuln',)


# admin.site.register(Vuln, SimpleHistoryAdmin)
admin.site.register(Vuln, VulnAdmin)
# admin.site.register(ExploitMetadata, SimpleHistoryAdmin)
admin.site.register(ExploitMetadata, ExploitAdmin)
# admin.site.register(ThreatMetadata, SimpleHistoryAdmin)
admin.site.register(ThreatMetadata, ThreatAdmin)
