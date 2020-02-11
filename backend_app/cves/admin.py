from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import CVE, CPE, CWE, Bulletin

admin.site.register(CVE, SimpleHistoryAdmin)
admin.site.register(CPE)
admin.site.register(CWE)
admin.site.register(Bulletin, SimpleHistoryAdmin)
