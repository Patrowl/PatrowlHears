from django.db import models
from django.utils import timezone
# from django.conf import settings
# from django.core.mail import send_mail
from django.contrib.postgres.fields import JSONField, ArrayField
from common.utils.constants import EXPLOIT_AVAILABILITY, TRUST_LEVELS, TLP_LEVELS, EXPLOIT_MATURITY_LEVELS
# from django_celery_beat.models import PeriodicTask
from .tasks import send_email_message_task
import logging
logger = logging.getLogger(__name__)

RULE_SCOPE_ATTRIBUTES = {
    'vulns': {
        'cvss2_score': {"type": "numeric"},
        'is_exploitable': {"type": "list", "values": [True, False]},
        'is_in_the_news': {"type": "list", "values": [True, False]},
        'is_remote': {"type": "list", "values": [True, False]},
        # 'name':         {"type": "text"},
        # 'type':         {"type": "list", "values": ['ip', 'domain', 'url']},
    },
    'exploits': {
        'availability': {
            "type": "list",
            "values": [x[0] for x in EXPLOIT_AVAILABILITY]
        },
        'trust_level': {
            "type": "list",
            "values": [x[0] for x in TRUST_LEVELS]
        },
        'maturity': {
            "type": "list",
            "values": [x[0] for x in EXPLOIT_MATURITY_LEVELS]
        },
        'tlp_level': {
            "type": "list",
            "values": [x[0] for x in TLP_LEVELS]
        }
    }
}

RULE_ACTIONS = (
    ('debug',   'Debug'),
    ('event',   'PatrowlHears event'),
    ('logfile', 'Logfile'),
    ('email',   'Email'),
    ('thehive', 'TheHive alert'),
    ('twitter', 'Twitter message'),
    ('slack',   'Slack message'),
    ('splunk',   'Splunk message'),
)

RULE_TYPES = (
    ('ondemand', 'On-demand'),
    ('auto',     'Automatic'),
    ('periodic', 'Periodic'),  # frequency ?
)

RULE_CONDITIONS = {
    'text': {
        "__iexact":      "is exactly",
        "__icontains":   "contains",
        "__istartswith": "starts with",
        "__iendswith":   "ends with",
    },
    'numeric': {
        "__gt":  "greater than",
        "__gte": "greater than/equal to",
        "__lt":  "less than",
        "__lte": "less than/equal to",
    },
    'list': None,  # see values
}

RULE_SEVERITIES = (
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
)

RULE_TARGETS = [
    ('add_vuln', 'New vulnerability'),
    ('update_vuln', 'Change(s) in vulnerability'),
    ('add_exploit', 'New exploit'),
    ('update_exploit', 'Change(s) in exploit')
]


class AlertingTemplate(models.Model):
    name = models.CharField(max_length=256, default='Default template')
    action = models.CharField(choices=RULE_ACTIONS, default='debug', max_length=10)
    canvas = models.CharField(default='n/a', max_length=50)

    class Meta:
        db_table = 'alerting_templates'

    def __str__(self):
        return "{} / {}".format(self.id, self.name)


class AlertingRule(models.Model):
    title = models.CharField(max_length=256, default='New alerting rule')
    target = models.CharField(choices=RULE_TARGETS, default='add_vuln', max_length=32)
    action = models.CharField(choices=RULE_ACTIONS, default='debug', max_length=10)
    conditions = JSONField(default=dict, null=True, blank=True)
    check_fields = ArrayField(
        models.CharField(default='', max_length=64), null=True, blank=True
    )
    # type = models.CharField(choices=RULE_TYPES, default='ondemand', max_length=10)
    # periodic_task    = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.CASCADE)
    severity = models.CharField(choices=RULE_SEVERITIES, default='Low', max_length=10)
    template = models.ForeignKey(AlertingTemplate, null=True, blank=True, on_delete=models.CASCADE)
    on_monitored = models.BooleanField(default=False)
    in_bulk = models.BooleanField(default=False)
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'alerting_rules'

    def __str__(self):
        return "{} / {} / {} / {}".format(
            self.id, self.target, self.action, self.title)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.updated_at = timezone.now()
        return super(AlertingRule, self).save(*args, **kwargs)

    def notify(self, short="", long=""):
        if self.action == 'debug':
            print("[Alert Notification][Debug] short: {}, long: {}". format(short, long))
            logger.debug("short: {}, long: {}". format(short, long))
        elif self.action == 'email':
            print("[Alert Notification][Mail] short: {}, long: {}". format(short, long))
            print("loooong:", long)
            send_email_message_task.apply_async(args=[short, long], queue='default', retry=False)
        # elif self.action == 'twitter':
        #     send_twitter_message(self, message)
        # elif self.action == 'slack':
        #     send_slack_message(self, message)
        # elif self.action == 'thehive':
        #     send_thehive_message(self, message, asset, description)
        # elif self.action == 'event':
        #     Event.objects.create(
        #         message="[Alert][Rule={}]{}".format(self.title, message),
        #         type="ALERT", severity="INFO")
