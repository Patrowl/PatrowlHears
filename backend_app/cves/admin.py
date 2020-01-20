from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import CVE, CPE, CWE, Bulletin

admin.site.register(CVE, SimpleHistoryAdmin)
admin.site.register(CPE, SimpleHistoryAdmin)
admin.site.register(CWE, SimpleHistoryAdmin)
admin.site.register(Bulletin, SimpleHistoryAdmin)
