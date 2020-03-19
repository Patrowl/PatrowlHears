from django.contrib.auth.models import AbstractUser
from django.db import models
from organizations.models import Organization


class User(AbstractUser):
    pass


class ServiceProvider(Organization):
    """Now this model has a name field and a slug field."""

    email = models.EmailField()


class Client(Organization):
    """Now this model has a name field and a slug field."""

    description = models.TextField()
    email = models.EmailField()
    service_provider = models.ForeignKey(
        ServiceProvider, related_name="clients", on_delete=models.CASCADE)

    objects = models.Manager()
