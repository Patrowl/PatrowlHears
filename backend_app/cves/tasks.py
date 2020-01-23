from celery import shared_task, group
from common.utils import cvesearch

import logging
logger = logging.getLogger(__name__)
MAX_CONCURRENT_TASKS = 10


@shared_task(bind=True, acks_late=True)
def sync_cwes_task(self):
    logger.debug("Entering 'sync_cwes_task'")
    cvesearch.sync_cwes_fromdb()
    return True


@shared_task(bind=True, acks_late=True)
def sync_cpes_task(self):
    logger.debug("Entering 'sync_cwes_task'")
    cvesearch.sync_cpes_fromdb()
    return True


@shared_task(bind=True, acks_late=True)
def sync_cves_task(self):
    logger.debug("Entering 'sync_cves_task'")
    cvesearch.sync_cves_fromdb()
    return True


@shared_task(bind=True, acks_late=True)
def sync_vias_task(self):
    logger.debug("Entering 'sync_vias_task'")
    cvesearch.sync_via_fromdb()
    return True

#
# @shared_task(bind=True, acks_late=True)
# def sync_via_exploits_task(self):
#     logger.debug("Entering 'sync_via_exploits_task'")
#     cvesearch.sync_exploits_fromvia()
#     return True
