from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import CVE, CPE, CWE, Bulletin, Vendor, Product, ProductVersion, Package, PackageType


class ProductsInline(admin.TabularInline):
    model = CVE.products.through
    raw_id_fields = ("product",)


class ProductVersionsInline(admin.TabularInline):
    model = CVE.productversions.through
    raw_id_fields = ("productversion",)


class BulletinsInline(admin.TabularInline):
    model = CVE.bulletins.through
    raw_id_fields = ("bulletin",)


class CVEAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('cwe',)
    exclude = ('products', 'productversions', 'bulletins',)
    inlines = (ProductsInline, ProductVersionsInline, BulletinsInline,)


class CPEAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('vendor', 'product',)


class ProductAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('vulns', 'vendor',)


class ProductVersionAdmin(SimpleHistoryAdmin):
    raw_id_fields = ('product',)


admin.site.register(CVE, CVEAdmin)
# admin.site.register(CVE, SimpleHistoryAdmin)
admin.site.register(Vendor, SimpleHistoryAdmin)
# admin.site.register(Product, SimpleHistoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVersion, ProductVersionAdmin)
# admin.site.register(ProductVersion, SimpleHistoryAdmin)
admin.site.register(CPE, CPEAdmin)
admin.site.register(CWE)
admin.site.register(Bulletin, SimpleHistoryAdmin)
admin.site.register(Package)
admin.site.register(PackageType)
