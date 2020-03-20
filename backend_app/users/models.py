from django.contrib.auth.models import AbstractUser
from django.db import models
# from organizations.models import Organization
from vulns.models import Vuln
from cves.models import Product


class User(AbstractUser):
    # monitored_vulns = models.ManyToManyField(Vuln, related_name='monitoring_users')
    # monitored_products = models.ManyToManyField(Product, related_name='monitoring_users')
    pass

#
# class ServiceProvider(Organization):
#     """Now this model has a name field and a slug field."""
#
#     email = models.EmailField()
#
#
# class Client(Organization):
#     """Now this model has a name field and a slug field."""
#
#     description = models.TextField()
#     email = models.EmailField()
#     service_provider = models.ForeignKey(
#         ServiceProvider, related_name="clients", on_delete=models.CASCADE)
#
#     objects = models.Manager()
