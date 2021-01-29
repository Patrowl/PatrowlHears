from celery import shared_task
from django.conf import settings
from .utils import send_email_message
from backend_app import slack
from datetime import datetime
import json
import requests
import logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, acks_late=True)
def send_email_message_task(self, short, long, template, recipients):
    logger.debug("Entering 'send_email_message_task'")
    send_email_message(short, long, template, recipients)
    return True


@shared_task(bind=True, acks_late=True)
def send_slack_message_task(self, message, apitoken, channel):
    logger.debug("Entering 'send_slack_message_task'")
    slack.send_slack_message(message, apitoken, channel)
    return True


@shared_task(bind=True, acks_late=True)
def slack_alert_vuln_task(self, vuln_id, type="new"):
    from vulns.models import Vuln
    from organizations.models import Organization

    logger.debug("Entering 'slack_alert_vuln_task'")
    vuln = Vuln.objects.filter(id=vuln_id).first()
    if vuln is None:
        return False

    if type == "update":
        prefix = "PatrowlHears // Vulnerability changes detected ! {}, Score: {}".format(vuln.cveid, vuln.score)
    else:
        prefix = "PatrowlHears // New vulnerability found ! {}, Score: {}".format(vuln.cveid, vuln.score)
    curr_date = datetime.now().strftime("%B %d,%Y - %H:%M:%S")
    vuln_link = "<{}/#/vulns/{}|Direct link>".format(settings.BASE_URL, vuln.id)
    vuln_exploit_count = vuln.exploitmetadata_set.count()
    #@Todo: add organization exploits

    metrics = "\
        - Is Exploitable? {}\n\
        - Is Confirmed? {}\n\
        - In the Wild? {}\n\
        - In the News? {}".format(
        vuln.is_exploitable,
        vuln.is_confirmed,
        vuln.is_in_the_news,
        vuln.is_in_the_wild
    )

    affected_products = ", ".join(["*{}* ({})".format(p.name.replace('_', ' ').title(), p.vendor.name.replace('_', ' ').title()) for p in vuln.products.all()])

    for org in Organization.objects.all():
        if org.org_settings.alerts_slack_enabled is True and org.org_settings.alerts_slack['update_vuln'] is True and org.org_settings.alerts_slack['url'] != "":
            webhook_url = org.org_settings.alerts_slack['url']
            # slack_data = {'text': "Vulnerability changes detected: [PH-{}@{}] {}".format(vuln.id, vuln.score, vuln.summary)}
            banner = "[{}] *{}* - Score:*{}* - Exploits:*{}* - CVSSv2:*{}*".format(
                vuln_link,
                vuln.cveid,
                vuln.score,
                vuln_exploit_count + vuln.orgexploitmetadata_set.count(),
                vuln.cvss
            )

            slack_data = {
                "text": prefix,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "{}\n>{}\n{}".format(banner, vuln.summary, metrics)
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Affected products: {}".format(affected_products)
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "Last updated: {} by *PatrowlHears Slack alerting*".format(curr_date)
                            }
                        ]
                    }
                ]
            }
            try:
                response = requests.post(
                    webhook_url, data=json.dumps(slack_data),
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code != 200:
                    raise ValueError(
                        'Request to slack returned an error %s, the response is:\n%s'
                        % (response.status_code, response.text)
                    )
            except Exception as e:
                logger.error(e)
    return True
#
# {
# 	"blocks": [
# 		{
# 			"type": "section",
# 			"text": {
# 				"type": "mrkdwn",
# 				"text": "[<https://hears.patrowl.io/#/vuln/21324|PH-21324>][Score=80][E=3] CVE-2020-2222\n>qsoshdfkusgd"
# 			}
# 		},
# 		{
# 			"type": "context",
# 			"elements": [
# 				{
# 					"type": "mrkdwn",
# 					"text": "Last updated: Jan 1, 2019"
# 				}
# 			]
# 		}
# 	]
# }
