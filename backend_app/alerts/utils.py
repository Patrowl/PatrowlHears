from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from backend_app import twitter_api
import logging
logger = logging.getLogger(__name__)


def send_email_message(subject="", body={}, template="vuln", recipients=[]):
    tmpl_txt = "{}.txt".format(template)
    tmpl_html = "{}.html".format(template)
    msg_text = render_to_string(tmpl_txt, {'data': body})
    msg_html = render_to_string(tmpl_html, {'data': body})

    if subject in ["", None]:
        subject = '[PatrowlFeeds-Alert] ' + subject
    from_email = settings.EMAIL_HOST_USER
    try:
        msg = EmailMultiAlternatives(subject, msg_text, from_email, recipients)
        msg.attach_alternative(msg_html, "text/html")
        msg.send()
    except Exception as e:
        logger.error('Unable to send Email message:', e)
        return False
    return True


# https://python-twitter.readthedocs.io/en/latest/twitter.html#twitter.api.Api.PostUpdate
def send_tweet_message(message=""):
    # TWEET_CHARACTER_LIMIT = 280
    twitter_api.PostUpdate(status=message)
    logger.info('Tweet posted:', message)
