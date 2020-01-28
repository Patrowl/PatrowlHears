from celery import shared_task
from .utils import send_email_message, send_slack_message
import logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, acks_late=True)
def send_email_message_task(self, short, long):
    logger.debug("Entering 'send_email_message_task'")
    send_email_message(short, long)
    return True


@shared_task(bind=True, acks_late=True)
def send_slack_message_task(self, short, long):
    logger.debug("Entering 'send_slack_message_task'")
    send_slack_message(short, long)
    return True
