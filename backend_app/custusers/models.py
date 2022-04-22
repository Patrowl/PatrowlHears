from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords
from common.utils import _json_serial
import json

USER_TYPES = (
    ('DEFAULT', 'DEFAULT'),
    ('API', 'API'),
    ('WEB', 'WEB')
)


def user_profile_dict():
    return {
        'name': 'default',
        'version': '1',
        'monitored_items': -1,  # -1 = unlimited
        'manage_metadata': True,
        'manage_organization': False,
        'organization_users': -1,  # -1 = unlimited
        'manage_alert_email': True,
        'manage_alert_slack': True,
        'api_create_token': True,
        'api_throttle_rate': 'unlimited',    # -1 = unlimited
        'enable_server_datasync': True
    }


class User(AbstractUser):
    profile = models.JSONField(default=user_profile_dict, null=True)
    type = models.CharField(max_length=10, choices=USER_TYPES, default='DEFAULT')
    mfa_enabled = models.BooleanField(default=False)
    changed_first_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()

        return super(User, self).save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'type': self.type,
            'mfa_enabled': self.mfa_enabled,
            'changed_first_password': self.changed_first_password,
            'profile': self.profile,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, default=_json_serial)
