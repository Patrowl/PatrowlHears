from celery import shared_task, group
from celery.result import allow_join_result
from monitored_assets.models import MonitoredAsset
from .utils import _refresh_metadata_cve

import logging
logger = logging.getLogger(__name__)
MAX_CONCURRENT_TASKS = 10


@shared_task(bind=True, acks_late=True)
def refresh_metadata_cve_task(self, cve_id):
    logger.debug("Entering 'refresh_metadata_cve_task' with args: '{}'".format(cve_id))
    _refresh_metadata_cve(cve_id)
    return True


@shared_task(bind=True, acks_late=True)
def refresh_monitored_cves_task(self):
    logger.debug("Entering 'refresh_monitored_cve_task'")
    cves = MonitoredAsset.objects.filter(type="CVE", status="monitoring").values_list("name", flat=True)
    job = group([refresh_metadata_cve_task.s(cve_id) for cve_id in cves])
    result = job.apply_async()
    with allow_join_result():
        return result.get()
