from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Vuln, ExploitMetadata, ThreatMetadata


class ProductsInline(admin.TabularInline):
    model = Vuln.products.through
    raw_id_fields = ("product",)


class ProductVersionsInline(admin.TabularInline):
    model = Vuln.productversions.through
    raw_id_fields = ("productversion",)


class PackagesInline(admin.TabularInline):
    model = Vuln.packages.through
    raw_id_fields = ("package",)


class VulnAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('cve', 'cwe',)
    exclude = ('products', 'productversions', 'packages',)
    inlines = (ProductsInline, ProductVersionsInline, PackagesInline, )


class ExploitAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('vuln',)


class ThreatAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('vuln',)


admin.site.register(Vuln, VulnAdmin)
admin.site.register(ExploitMetadata, ExploitAdmin)
admin.site.register(ThreatMetadata, ThreatAdmin)
