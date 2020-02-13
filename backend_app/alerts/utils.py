from django.conf import settings
# from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import requests
import json
import logging
logger = logging.getLogger(__name__)


def send_email_message(short="", long={}, template="vuln"):
    tmpl_txt = "{}.txt".format(template)
    tmpl_html = "{}.html".format(template)
    msg_text = render_to_string(tmpl_txt, {'data': long})
    msg_html = render_to_string(tmpl_html, {'data': long})
    # contact_mail = Setting.objects.get(key="alerts.endpoint.email").value
    # send_mail(
    #     '[PatrowlFeeds] New alert: '+short,
    #     'Message: {}\nDescription: {}'.format(short, long),
    #     settings.EMAIL_HOST_USER,
    #     [settings.EMAIL_RCPT_USER],
    #     fail_silently=False,
    # )

    subject = '[PatrowlFeeds-Alert]'+short
    from_email, to = settings.EMAIL_HOST_USER, settings.EMAIL_RCPT_USER
    try:
        msg = EmailMultiAlternatives(subject, msg_text, from_email, [to])
        msg.attach_alternative(msg_html, "text/html")
        msg.send()
    except Exception as e:
        logger.error('Unable to send Email message:', e)
        return False
    return True


def send_slack_message(short="", long={}):
    slack_url = settings.ALERTING_SLACK_URL
    slack_channel = settings.ALERTING_SLACK_CHANNEL

    alert_message = '[PatrowlFeeds-Alert]'+short
    data_payload = {'text': alert_message, 'channel': slack_channel}
    try:
        requests.post(
            slack_url.value,
            data=json.dumps(data_payload),
            headers={'content-type': 'application/json'})
    except Exception as e:
        logger.error('Unable to send Slack message:', e)
        return False
    return True
