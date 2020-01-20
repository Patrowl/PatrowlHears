from celery import shared_task, group
from celery.result import allow_join_result
from common.utils import cvesearch

import logging
logger = logging.getLogger(__name__)
MAX_CONCURRENT_TASKS = 10


@shared_task(bind=True, acks_late=True)
def sync_cwes_task(self):
    logger.debug("Entering 'sync_cwes_task'")
    cvesearch.sync_cwe_fromdb()
    return True


@shared_task(bind=True, acks_late=True)
def sync_cpes_task(self):
    logger.debug("Entering 'sync_cwes_task'")
    cvesearch.sync_cpe_fromdb()
    return True


@shared_task(bind=True, acks_late=True)
def sync_cves_task(self):
    logger.debug("Entering 'sync_cves_task'")
    cvesearch.sync_cve_fromdb()
    return True
