from celery import shared_task, group
from celery.result import allow_join_result
from organizations.models import Organization
from .models import Vuln
from alerts.apis import _get_monitored_products_report
from alerts.tasks import send_email_message_task

import logging
logger = logging.getLogger(__name__)
MAX_CONCURRENT_TASKS = 10


@shared_task(bind=True, acks_late=True)
def refresh_vuln_score_task(self, vuln_id):
    logger.debug("Entering 'refresh_vuln_score_task' with args: '{}'".format(vuln_id))
    vuln = Vuln.objects.filter(id=vuln_id).first()
    try:
        if vuln is not None:
            vuln.update_score()
            vuln.save()
    except Exception as e:
        logger.error("Something goes wrong in 'refresh_vuln_score_task' with args: '{}' - {}".format(vuln, str(e)))
    return True


@shared_task(bind=True, acks_late=True)
def refresh_vulns_score_task(self):
    logger.debug("Entering 'refresh_vulns_score_task'")
    vulns = Vuln.objects.all().order_by('-id')
    job = group([refresh_vuln_score_task.s(vuln.id) for vuln in vulns])
    result = job.apply_async()
    with allow_join_result():
        return result.get()


@shared_task(bind=True, acks_late=True)
def refresh_vuln_product_versions_task(self, vuln_id):
    logger.debug("Entering 'refresh_vuln_product_versions_task' with args: '{}'".format(vuln_id))
    vuln = Vuln.objects.filter(id=vuln_id).first()
    try:
        if vuln is not None:
            vuln.update_product_versions()
            vuln.save()
    except Exception as e:
        logger.error("Something goes wrong in 'refresh_vuln_product_versions_task' with args: '{}' - {}".format(vuln, str(e)))
    return True


@shared_task(bind=True, acks_late=True)
def refresh_vulns_product_versions_task(self):
    logger.debug("Entering 'refresh_vulns_product_versions_task'")
    vulns = Vuln.objects.all().order_by('-id')
    job = group([refresh_vuln_product_versions_task.s(vuln.id) for vuln in vulns])
    result = job.apply_async()
    with allow_join_result():
        return result.get()


@shared_task(bind=True, acks_late=True)
def email_daily_report_task(self):
    logger.debug("Entering 'email_daily_report_task'")
    for org in Organization.objects.all():
        if org.org_settings.alerts_emails_enabled is True and org.org_settings.enable_daily_email_report and len(org.org_settings.alerts_emails) > 0:
            mail_body = _get_monitored_products_report(org, delta_days=1, sendmail=False)
            mail_title = "Daily report"
            logger.info("Processing 'email_daily_report_task' for org: {}/{}".format(org.id, org.name))
            send_email_message_task.apply_async(
                args=[mail_title, mail_body, 'products_report', org.org_settings.alerts_emails],
                queue='alerts',
                retry=False
            )


@shared_task(bind=True, acks_late=True)
def email_weekly_report_task(self):
    logger.debug("Entering 'email_weekly_report_task'")
    for org in Organization.objects.all():
        if org.org_settings.alerts_emails_enabled is True and org.org_settings.enable_weekly_email_report and len(org.org_settings.alerts_emails) > 0:
            mail_body = _get_monitored_products_report(org, delta_days=7, sendmail=False)
            mail_title = "Weekly report"
            logger.info("Processing 'email_weekly_report_task' for org: {}/{}".format(org.id, org.name))
            send_email_message_task.apply_async(
                args=[mail_title, mail_body, 'products_report', org.org_settings.alerts_emails],
                queue='alerts',
                retry=False
            )


@shared_task(bind=True, acks_late=True)
def email_monthly_report_task(self):
    logger.debug("Entering 'email_monthly_report_task'")
    for org in Organization.objects.all():
        if org.org_settings.alerts_emails_enabled is True and org.org_settings.enable_monthly_email_report and len(org.org_settings.alerts_emails) > 0:
            mail_body = _get_monitored_products_report(org, delta_days=30, sendmail=False)
            mail_title = "Monthly report"
            logger.info("Processing 'email_monthly_report_task' for org: {}/{}".format(org.id, org.name))
            send_email_message_task.apply_async(
                args=[mail_title, mail_body, 'products_report', org.org_settings.alerts_emails],
                queue='alerts',
                retry=False
            )
