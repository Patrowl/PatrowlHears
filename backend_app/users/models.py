from django.contrib.auth.models import AbstractUser
from django.db import models
from organizations.models import OrganizationUser, Organization
from vulns.models import Vuln
from cves.models import Vendor, Product, ProductVersion
from annoying.fields import AutoOneToOneField


class User(AbstractUser):
    pass


class UserMonitoringList(models.Model):
    user = AutoOneToOneField(OrganizationUser, primary_key=True, on_delete=models.CASCADE, related_name='user_monitoring_list')
    vulns = models.ManyToManyField(Vuln, related_name='user_monitoring_list')
    products = models.ManyToManyField(Product, related_name='user_monitoring_list')

    class Meta:
        db_table = "user_monitoring_list"


class OrgMonitoringList(models.Model):
    organization = AutoOneToOneField(Organization, primary_key=True, on_delete=models.CASCADE, related_name='org_monitoring_list')
    vulns = models.ManyToManyField(Vuln, related_name='org_monitoring_list')
    vendors = models.ManyToManyField(Vendor, related_name='org_monitoring_list')
    products = models.ManyToManyField(Product, related_name='org_monitoring_list')
    productversions = models.ManyToManyField(ProductVersion, related_name='org_monitoring_list')

    class Meta:
        db_table = "org_monitoring_list"
