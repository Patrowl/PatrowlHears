from celery import shared_task, group
from celery.result import allow_join_result
from cves.models import CVE
from .models import Vuln
from .utils import _refresh_metadata_cve

import logging
logger = logging.getLogger(__name__)
MAX_CONCURRENT_TASKS = 10


@shared_task(bind=True, acks_late=True)
def refresh_vuln_score_task(self, vuln):
    logger.debug("Entering 'refresh_vuln_score_task' with args: '{}'".format(vuln))
    # vuln = Vuln.objects.filter(id=vuln_id).first()
    try:
        if vuln is not None:
            vuln.update_score()
            vuln.save()
    except Exception:
        logger.error("Something goes wrong in 'refresh_vuln_score_task' with args: '{}'".format(vuln))
    return True


@shared_task(bind=True, acks_late=True)
def refresh_vulns_score_task(self):
    logger.debug("Entering 'refresh_vulns_score_task'")
    vulns = Vuln.objects.all()
    job = group([refresh_vuln_score_task.s(vuln.id) for vuln in vulns])
    result = job.apply_async()
    with allow_join_result():
        return result.get()

# 
# @shared_task(bind=True, acks_late=True)
# def refresh_metadata_cve_task(self, cve_id):
#     logger.debug("Entering 'refresh_metadata_cve_task' with args: '{}'".format(cve_id))
#     _refresh_metadata_cve(cve_id)
#     return True
#

# @shared_task(bind=True, acks_late=True)
# def refresh_monitored_cves_task(self):
#     logger.debug("Entering 'refresh_monitored_cve_task'")
#     cves = CVE.objects.filter(monitored=True).values_list("name", flat=True)
#     job = group([refresh_metadata_cve_task.s(cve_id) for cve_id in cves])
#     result = job.apply_async()
#     with allow_join_result():
#         return result.get()
