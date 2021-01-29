from celery import shared_task
from django.conf import settings
from pymongo import MongoClient
from celery import group
from common.utils import cvesearch
import datetime
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
def sync_cve_task(self, cve_id):
    logger.debug("Entering 'sync_cve_task'")
    logger.info('Syncing {}'.format(cve_id))
    cvesearch.sync_cve_fromdb(cve_id)
    return True


@shared_task(bind=True, acks_late=True)
def sync_cves_task(self, from_year=1999, to_year=None):
    logger.debug("Entering 'sync_cves_task'")
    cli = MongoClient(
        settings.DATABASES['mongodb']['HOST'],
        settings.DATABASES['mongodb']['PORT'])
    db = cli['cvedb']
    cves = db.cves

    # Workaround for pymongo.errors.CursorNotFound fucking errors
    # search CVE by year and first id
    current_year = datetime.datetime.now().year
    if to_year is not None:
        current_year = int(to_year)
    for y in range(int(from_year), int(current_year)+1):
        for fi in range(0, 10):
            cursor_cve = []
            cursor_cve = cves.find({'id': {'$regex': '^CVE-{}-{}'.format(y, fi)}}, {'id': 1})
            cveid_list = [c['id'] for c in cursor_cve]
            if len(cveid_list) == 0:
                cursor_cve.close()
                continue
            try:
                job = group(sync_cve_task.s(cveid) for cveid in cveid_list)()
            except Exception as e:
                logger.error("Sommething gone wrong in sync_cves_atyear_task()")
                logger.error(e)
            finally:
                cursor_cve.close()

    return True


@shared_task(bind=True, acks_late=True)
def sync_cves_fromyear_task(self, from_year):
    logger.debug("Entering 'sync_cves_fromyear_task'")
    cvesearch.sync_cves_fromdb(from_year=from_year)
    return True

#
# @shared_task(bind=True, acks_late=True)
# def sync_cves_atyear_task(self, year):
#     logger.debug("Entering 'sync_cves_atyear_task'")
#     cvesearch.sync_cves_fromdb(from_year=year, to_year=year)
#     return True


@shared_task(bind=True, acks_late=True)
def sync_cves_atyear_task(self, year):
    logger.debug("Entering 'sync_cves_atyear_task'")

    cli = MongoClient(
        settings.DATABASES['mongodb']['HOST'],
        settings.DATABASES['mongodb']['PORT'])
    db = cli['cvedb']
    cves = db.cves

    # Workaround for pymongo.errors.CursorNotFound fucking errors
    # search CVE by year and first id
    for y in [year]:
        for fi in range(0, 10):
            cursor_cve = []
            cursor_cve = cves.find({'id': {'$regex': '^CVE-{}-{}'.format(y, fi)}}, {'id': 1})
            cveid_list = [c['id'] for c in cursor_cve]
            if len(cveid_list) == 0:
                cursor_cve.close()
                continue
            try:
                job = group(sync_cve_task.s(cveid) for cveid in cveid_list)()
            except Exception as e:
                logger.error("Sommething gone wrong in sync_cves_atyear_task()")
                logger.error(e)
            finally:
                cursor_cve.close()
            # cursor_cve.close()
    # return True
    # cvesearch.sync_cves_fromdb(from_year=year, to_year=year)
    return True


@shared_task(bind=True, acks_late=True)
def sync_vias_task(self):
    logger.debug("Entering 'sync_vias_task'")
    cvesearch.sync_via_fromdb()
    return True


@shared_task(bind=True, acks_late=True)
def sync_bulletins_task(self):
    logger.debug("Entering 'sync_bulletins_task'")
    cvesearch.sync_bulletins_fromdb()
    return True

#
# @shared_task(bind=True, acks_late=True)
# def sync_via_exploits_task(self):
#     logger.debug("Entering 'sync_via_exploits_task'")
#     cvesearch.sync_exploits_fromvia()
#     return True
