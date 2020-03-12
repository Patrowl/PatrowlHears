from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import CVE, CPE, CWE, Bulletin, Vendor, Product, ProductVersion

class ProductAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('vulns',)

admin.site.register(CVE, SimpleHistoryAdmin)
admin.site.register(Vendor, SimpleHistoryAdmin)
# admin.site.register(Product, SimpleHistoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVersion, SimpleHistoryAdmin)
admin.site.register(CPE)
admin.site.register(CWE)
admin.site.register(Bulletin, SimpleHistoryAdmin)
