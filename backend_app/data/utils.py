from django.conf import settings
from cves.models import CVE, CPE, CWE, Vendor, Product, ProductVersion, Bulletin
from vulns.models import Vuln, ExploitMetadata, ThreatMetadata
from common.utils import get_field_data
from .models import DataSyncJob, DataSync

import datetime
import json
import logging
import math
import requests
logger = logging.getLogger(__name__)


'''
Steps:
- Check the 'since' parameter. By default, set it to the basedate setting
- Check the 'to' parameter. By default, set today
- Go into model (table) and check the oldest and the latest update dates
'''
def _export_data_info_model(model_class, model_name, since=None, to=None, from_id=None):
    if since is None:
        # export_since = datetime.datetime.now() - datetime.timedelta(days=1)
        export_since = datetime.datetime.strptime(settings.HEARS_DATASYNC_BASEDATE, '%Y-%m-%d')
    else:
        try:
            export_since = datetime.datetime.fromtimestamp(int(since))
        except Exception:
            return {"status": "error", "message": "'since' parameter is invalid. Use '%s' (Unix epoch format)"}

    if to is None:
        export_to = datetime.datetime.now()
    else:
        try:
            export_to = datetime.datetime.fromtimestamp(int(to))
        except Exception:
            return {"status": "error", "message": "'to' parameter is invalid. Use '%s' (Unix epoch format)"}

    model_filters = {
        'updated_at__gte': export_since,
        'updated_at__lte': export_to,
    }
    if from_id is not None:
        model_filters.update({'id__gte': from_id})
        # model_filters.update({'id__gt': int(from_id)})

    # Perform query
    # model_results = model_class.objects.filter(**model_filters).order_by('updated_at', 'id')
    model_results = model_class.objects.filter(**model_filters)

    return {
        model_name: {
            'count': model_results.count(),
            'oldest_id': get_field_data(model_results.order_by('id'), index=0, field='id'),
            'oldest_update': get_field_data(model_results.order_by('updated_at'), index=0, field='updated_at'),
            'latest_id': get_field_data(model_results.order_by('id'), index=-1, field='id'),
            'latest_update': get_field_data(model_results.order_by('updated_at'), index=-1, field='updated_at'),
        }
    }


def _export_data_model(model_class, model_name, since=None, to=None, from_id=None, chunk_size=None):
    if chunk_size is None:
        chunk_size = int(settings.HEARS_DATASYNC_CHUNKSIZE)
    else:
        chunk_size = int(chunk_size)

    if since is None:
        export_since = datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        try:
            export_since = datetime.datetime.fromtimestamp(int(since))
        except Exception:
            return {
                "status": "error",
                "message": "'since' parameter is invalid. Use '%s' (Unix epoch format)"
            }

    if to is None:
        export_to = datetime.datetime.now()
    else:
        try:
            export_to = datetime.datetime.fromtimestamp(int(to))
        except Exception:
            return {
                "status": "error",
                "message": "'to' parameter is invalid. Use '%s' (Unix epoch format)"
            }

    model_results = []
    last_update = export_since
    model_filters = {
        'updated_at__gte': export_since,
        'updated_at__lte': export_to,
    }
    if from_id is not None:
        model_filters.update({'id__gte': int(from_id)})
        # model_filters.update({'id__gt': int(from_id)})

    last_id = from_id
    # for model_instance in model_class.objects.filter(**model_filters).order_by('updated_at', 'id')[:chunk_size]:
    for model_instance in model_class.objects.filter(**model_filters).order_by('id')[:chunk_size]:
        model_results.append(model_instance.to_dict())
        last_id = model_instance.id
        if model_instance.updated_at > last_update:
            last_update = model_instance.updated_at

    return {
        model_name: model_results,
        'export_since': export_since,
        'export_to': export_to,
        'count': len(model_results),
        'last_id': last_id,
        'last_update': last_update,
        'last_update_epoch': last_update.strftime('%s'),
    }


'''
Steps:
- Check the 'since' parameter. By default, it's set to yesterday
- Check the 'to' parameter. By default, it's set to today
- Go into relevant models (tables) and check the oldest and the latest date updates
'''
def _export_data_info(since=None, to=None):

    if since is None:
        export_since = datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        try:
            export_since = datetime.datetime.fromtimestamp(int(since))
        except Exception:
            return {"status": "error", "message": "'since' parameter is invalid. Use '%s' (Unix epoch format)"}

    if to is None:
        export_to = datetime.datetime.now()
    else:
        try:
            export_to = datetime.datetime.fromtimestamp(int(to))
        except Exception:
            return {"status": "error", "message": "'to' parameter is invalid. Use '%s' (Unix epoch format)"}

    kb_cwe = CWE.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    kb_cpe = CPE.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    kb_cve = CVE.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    kb_vendor = Vendor.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    kb_product = Product.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    kb_product_version = ProductVersion.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    kb_bulletin = Bulletin.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    vulns = Vuln.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    exploits = ExploitMetadata.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')
    threats = ThreatMetadata.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')

    data = {
        'kb_cwe': {
            'count': kb_cwe.count(),
            'oldest_update': get_field_data(kb_cwe, index=0, field='updated_at'),
            'latest_update': get_field_data(kb_cwe, index=-1, field='updated_at'),
        },
        'kb_cpe': {
            'count': kb_cpe.count(),
            'oldest_update': get_field_data(kb_cpe, index=0, field='updated_at'),
            'latest_update': get_field_data(kb_cpe, index=-1, field='updated_at'),
        },
        'kb_cve': {
            'count': kb_cve.count(),
            'oldest_update': get_field_data(kb_cve, index=0, field='updated_at'),
            'latest_update': get_field_data(kb_cve, index=-1, field='updated_at'),
        },
        'kb_vendor': {
            'count': kb_vendor.count(),
            'oldest_update': get_field_data(kb_vendor, index=0, field='updated_at'),
            'latest_update': get_field_data(kb_vendor, index=-1, field='updated_at'),
        },
        'kb_product': {
            'count': kb_product.count(),
            'oldest_update': get_field_data(kb_product, index=0, field='updated_at'),
            'latest_update': get_field_data(kb_product, index=-1, field='updated_at'),
        },
        'kb_product_version': {
            'count': kb_product_version.count(),
            'oldest_update': get_field_data(kb_product_version, index=0, field='updated_at'),
            'latest_update': get_field_data(kb_product_version, index=-1, field='updated_at'),
        },
        'kb_bulletin': {
            'count': kb_bulletin.count(),
            'oldest_update': get_field_data(kb_bulletin, index=0, field='updated_at'),
            'latest_update': get_field_data(kb_bulletin, index=-1, field='updated_at'),
        },
        'vulns': {
            'count': vulns.count(),
            'oldest_update': get_field_data(vulns, index=0, field='updated_at'),
            'latest_update': get_field_data(vulns, index=-1, field='updated_at'),
        },
        'exploits': {
            'count': exploits.count(),
            'oldest_update': get_field_data(exploits, index=0, field='updated_at'),
            'latest_update': get_field_data(exploits, index=-1, field='updated_at'),
        },
        'threats': {
            'count': threats.count(),
            'oldest_update': get_field_data(threats, index=0, field='updated_at'),
            'latest_update': get_field_data(threats, index=-1, field='updated_at'),
        }
    }
    total = 0
    oldest_update = export_to
    latest_update = export_since
    for k, v in data.items():
        total += v['count']
        if k != 'vulns':  # Do not take update date of vulns into account. See calculated and temporal-based attributes as 'score'
            if v['oldest_update'] is not None and v['oldest_update'] < oldest_update:
                oldest_update = v['oldest_update']
            if v['latest_update'] is not None and v['latest_update'] > latest_update:
                latest_update = v['latest_update']

    data.update({
        'since': export_since,
        'to': export_to,
        'total': total,
        'oldest_update': oldest_update,
        'oldest_update_epoch': int(oldest_update.strftime('%s')),
        'latest_update': latest_update,
        'latest_update_epoch': int(latest_update.strftime('%s')),
    })
    return data


def _export_data(limit=100, since=None, to=None):

    if since is None:
        export_since = datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        try:
            export_since = datetime.datetime.fromtimestamp(int(since))
        except Exception:
            return {
                "status": "error",
                "message": "'since' parameter is invalid. Use '%s' (Unix epoch format)"
            }

    if to is None:
        export_to = datetime.datetime.now()
    else:
        try:
            export_to = datetime.datetime.fromtimestamp(int(to))
        except Exception:
            return {
                "status": "error",
                "message": "'to' parameter is invalid. Use '%s' (Unix epoch format)"
            }

    kb_cwe = []
    kb_cpe = []
    kb_cve = []
    kb_vendor = []
    kb_product = []
    kb_product_version = []
    kb_bulletin = []
    vulns = []
    exploits = []
    threats = []
    last_update = export_since

    for cwe in CWE.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')[:limit]:
        kb_cwe.append(cwe.to_dict())
        if cwe.updated_at > last_update:
            last_update = cwe.updated_at

    for cpe in CPE.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')[:limit]:
        kb_cpe.append(cpe.to_dict())
        if cpe.updated_at > last_update:
            last_update = cpe.updated_at

    for bulletin in Bulletin.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')[:limit]:
        kb_bulletin.append(bulletin.to_dict())
        if bulletin.updated_at > last_update:
            last_update = bulletin.updated_at

    for vendor in Vendor.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')[:limit]:
        kb_vendor.append(vendor.to_dict())
        if vendor.updated_at > last_update:
            last_update = vendor.updated_at

        for product in vendor.product_set.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')[:limit]:
            kb_product.append(product.to_dict())
            if product.updated_at > last_update:
                last_update = product.updated_at

            for product_version in product.productversion_set.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')[:limit]:
                kb_product_version.append(product_version.to_dict())
                if product_version.updated_at > last_update:
                    last_update = product_version.updated_at

    for cve in CVE.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')[:limit]:
        kb_cve.append(cve.to_dict())
        if cve.updated_at > last_update:
            last_update = cve.updated_at

    for vuln in Vuln.objects.filter(updated_at__gte=export_since, updated_at__lte=export_to).order_by('updated_at')[:limit]:
        vulns.append(vuln.to_dict())
        if vuln.updated_at > last_update:
            last_update = vuln.updated_at

        for exploit in vuln.exploitmetadata_set.all():
            exploits.append(exploit.to_dict())
            if exploit.updated_at > last_update:
                last_update = exploit.updated_at

        for threat in vuln.threatmetadata_set.all():
            threats.append(threat.to_dict())
            if threat.updated_at > last_update:
                last_update = threat.updated_at

    export_data = {
        'kb_cwe': kb_cwe,
        'kb_cpe': kb_cpe,
        'kb_cve': kb_cve,
        'kb_vendor': kb_vendor,
        'kb_product': kb_product,
        'kb_product_version': kb_product_version,
        'kb_bulletin': kb_bulletin,
        'vulns': vulns,
        'exploits': exploits,
        'threats': threats,
        'export_since': export_since,
        'export_to': export_to,
        'last_update': last_update,
        'last_update_epoch': last_update.strftime('%s'),
    }

    return export_data


def _import_data(data, verbose=False):
    stats = {}
    success = []
    errors = []

    nbok = 0
    nbnok = 0
    if 'kb_cwe' in data.keys():
        for i_cwe in data['kb_cwe']:
            if verbose is True:
                print("Processing: CWE/{}".format(i_cwe['id']))
            try:
                cwe = CWE.objects.get(id=i_cwe['id'])
            except CWE.DoesNotExist:
                cwe = CWE.objects.create(id=i_cwe['id'])

            for attr, value in i_cwe.items():
                setattr(cwe, attr, value)

            try:
                cwe.save(touch=False)
                success.append({'kb_cwe': i_cwe['id']})
                nbok += 1
            except Exception:
                errors.append({'kb_cwe': i_cwe})
                nbnok += 1
    stats.update({'kb_cwe': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'kb_bulletin' in data.keys():
        for i_bulletin in data['kb_bulletin']:
            try:
                bulletin = Bulletin.objects.get(id=i_bulletin['id'])
            except Bulletin.DoesNotExist:
                bulletin = Bulletin.objects.create(id=i_bulletin['id'])

            for attr, value in i_bulletin.items():
                setattr(bulletin, attr, value)

            try:
                bulletin.save(touch=False)
                success.append({'kb_bulletin': i_bulletin['id']})
                nbok += 1
            except Exception:
                errors.append({'kb_bulletin': i_bulletin})
                nbnok += 1
                break
    stats.update({'kb_bulletin': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'kb_vendor' in data.keys():
        for i_vendor in data['kb_vendor']:
            # print("id:", i_vendor['id'], "name:", i_vendor['name'])
            try:
                vendor = Vendor.objects.get(id=i_vendor['id'])
            except Vendor.DoesNotExist:
                # print("Not exists, trying to create another one", i_vendor)
                vendor = Vendor.objects.create(id=i_vendor['id'], name=i_vendor['name'])

            for attr, value in i_vendor.items():
                setattr(vendor, attr, value)

            try:
                # print("ok")
                vendor.save(touch=False)
                success.append({'kb_vendor': i_vendor['id']})
                nbok += 1
            except Exception as e:
                print(e)
                errors.append({'kb_vendor': i_vendor})
                nbnok += 1
    stats.update({'kb_vendor': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'kb_product' in data.keys():
        for i_product in data['kb_product']:
            # print("i_product:", i_product)
            try:
                product = Product.objects.get(id=i_product['id'])
            except Product.DoesNotExist:
                # print("Not exists, trying to create another one", i_product)
                product = Product.objects.create(
                    id=i_product['id'],
                    name=i_product['name'],
                    vendor_id=i_product['vendor_id'])

            # print("product av:", product)

            for attr, value in i_product.items():
                if attr != 'vendor':
                    setattr(product, attr, value)
            # print("product ap:", product)

            try:
                product.save(touch=False)
                success.append({'kb_product': i_product['id']})
                nbok += 1
            except Exception:
                errors.append({'kb_product': i_product})
                nbnok += 1
    stats.update({'kb_product': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'kb_product_version' in data.keys():
        for i_productversion in data['kb_product_version']:
            try:
                productversion = ProductVersion.objects.get(id=i_productversion['id'])
            except ProductVersion.DoesNotExist:
                productversion = ProductVersion.objects.create(
                    id=i_productversion['id'],
                    product_id=i_productversion['product_id'],
                    vector=i_productversion['vector'],
                    version=i_productversion['version']
                )

            for attr, value in i_productversion.items():
                if attr not in ['product', 'vendor']:
                    setattr(productversion, attr, value)

            try:
                productversion.save(touch=False)
                success.append({'kb_product_version': i_productversion['id']})
                nbok += 1
            except Exception:
                errors.append({'kb_product_version': i_productversion})
                nbnok += 1
    stats.update({'kb_product_version': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'kb_cpe' in data.keys():
        for i_cpe in data['kb_cpe']:
            try:
                cpe = CPE.objects.get(id=i_cpe['id'])
            except CPE.DoesNotExist:
                cpe = CPE.objects.create(
                    id=i_cpe['id'],
                    vendor_id=i_cpe['vendor_id'],
                    product_id=i_cpe['product_id']
                )

            for attr, value in i_cpe.items():
                if attr not in ['product', 'vendor']:
                    setattr(cpe, attr, value)

            try:
                cpe.save(touch=False)
                success.append({'kb_cpe': i_cpe['id']})
                nbok += 1
            except Exception:
                errors.append({'kb_cpe': i_cpe})
                nbnok += 1
    stats.update({'kb_cpe': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'kb_cve' in data.keys():
        for i_cve in data['kb_cve']:
            try:
                cve = CVE.objects.get(id=i_cve['id'])
            except CVE.DoesNotExist:
                cve = CVE.objects.create(id=i_cve['id'])

            for attr, value in i_cve.items():
                if attr not in ['products', 'productversions', 'bulletins', 'cwe']:
                    setattr(cve, attr, value)
                if attr == 'cwe' and value not in [None, '']:
                    cve.cwe = CWE.objects.get(id=value)

            cve.products.set(i_cve['products'])
            cve.productversions.set(i_cve['productversions'])
            cve.bulletins.set(i_cve['bulletins'])

            try:
                cve.save(touch=False)
                success.append({'kb_cve': i_cve['id']})
                nbok += 1
            except Exception:
                errors.append({'kb_cve': i_cve})
                nbnok += 1
    stats.update({'kb_cve': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'vulns' in data.keys():
        for i_vuln in data['vulns']:
            try:
                vuln = Vuln.objects.get(id=i_vuln['id'])
            except Vuln.DoesNotExist:
                vuln = Vuln.objects.create(
                    id=i_vuln['id'],
                    published=datetime.datetime.strptime(i_vuln['published'], '%Y-%m-%d %H:%M:%S'))

            for attr, value in i_vuln.items():
                if attr not in ['products', 'productversions', 'cwe', 'cve', 'exploit_cnt', 'exploit_count', 'published']:
                    setattr(vuln, attr, value)
                if attr == 'cve' and value not in [None, '']:
                    vuln.cve = CVE.objects.get(id=value)
                if attr == 'cwe' and value not in [None, '']:
                    vuln.cwe = CWE.objects.get(id=value)

            vuln.products.set(i_vuln['products'])
            vuln.productversions.set(i_vuln['productversions'])

            try:
                vuln.save(touch=False)
                success.append({'vulns': i_vuln['id']})
                nbok += 1
            except Exception:
                errors.append({'vulns': i_vuln})
                nbnok += 1
    stats.update({'vulns': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'exploits' in data.keys():
        for i_exploit in data['exploits']:
            try:
                exploit = ExploitMetadata.objects.get(id=i_exploit['id'])
            except ExploitMetadata.DoesNotExist:
                exploit = ExploitMetadata.objects.create(id=i_exploit['id'])

            for attr, value in i_exploit.items():
                if attr not in ['vuln_id', 'vuln_uuid']:
                    setattr(exploit, attr, value)
                if attr == 'vuln_id' and value not in [None, '']:
                    exploit.vuln = Vuln.objects.get(id=value)

            try:
                exploit.save(touch=False)
                success.append({'exploits': i_exploit['id']})
                nbok += 1
            except Exception:
                errors.append({'exploits': i_exploit})
                nbnok += 1
    stats.update({'exploits': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    nbok = 0
    nbnok = 0
    if 'threats' in data.keys():
        for i_threat in data['threats']:
            try:
                threat = ThreatMetadata.objects.get(id=i_threat['id'])
            except ThreatMetadata.DoesNotExist:
                threat = ThreatMetadata.objects.create(id=i_threat['id'])

            for attr, value in i_threat.items():
                if attr not in ['vuln_id', 'vuln_uuid']:
                    setattr(threat, attr, value)
                if attr == 'vuln_id' and value not in [None, '']:
                    threat.vuln = Vuln.objects.get(id=value)

            try:
                threat.save(touch=False)
                success.append({'threats': i_threat['id']})
                nbok += 1
            except Exception:
                errors.append({'threats': i_threat})
                nbnok += 1
    stats.update({'threats': {'total': nbok+nbnok, 'imported': nbok, 'failed': nbnok}})

    results = {
        'stats': stats,
        'success': success,
        'errors': errors
    }
    return results


def _run_datasync_model(model_class, model_name, chunk_size=None, store=True):

    if chunk_size is None:
        chunk_size = int(settings.HEARS_DATASYNC_CHUNKSIZE)
    else:
        chunk_size = int(chunk_size)

    # Create a datasync job
    dsj = DataSyncJob.objects.create()

    # Search the basedate reference. First look in successful DataSync entries for this model
    last_valid_datasync = DataSync.objects.filter(
        status='finished',
        mdl_name=model_name,
        has_more_updates=False
        ).order_by('-to_date')
    # print("last_valid_datasync:", last_valid_datasync)

    # If no DataSync found, check the last time this model has been updated
    # locally. Otherwise, set the default basedate reference
    if len(last_valid_datasync) == 0:
        eaim = _export_data_info_model(
            model_class=model_class,
            model_name=model_name,
            since=datetime.datetime.strptime(settings.HEARS_DATASYNC_BASEDATE, '%Y-%m-%d').strftime('%s')
        )
        if eaim[model_name]['oldest_update'] is not None:
            basedate_since = eaim[model_name]['latest_update']
        else:
            basedate_since = datetime.datetime.strptime(settings.HEARS_DATASYNC_BASEDATE, '%Y-%m-%d')
    else:
        basedate_since = last_valid_datasync[0].to_date

    # print(basedate_since, basedate_since.strftime('%s'))
    end_date = datetime.datetime.today()

    # Initialize requests session
    baseurl = settings.HEARS_DATASYNC_URL
    rs = requests.Session()
    rs.headers['Authorization'] = 'Token {}'.format(settings.HEARS_DATASYNC_AUTHTOKEN)
    rs.proxies = settings.PROXIES
    rs.verify = settings.HEARS_DATASYNC_SSLVERIFY
    rs.timeout = settings.HEARS_DATASYNC_TIMEOUT
    res = {}

    has_more_updates = True
    from_id = None
    # latest_update_date = ""
    nb_steps_total = 1
    nb_steps_done = 0

    while has_more_updates:
        try:
            # Search updates info for this model
            info_url = "{}/api/data/export/info?model={}&since={}&to={}".format(
                baseurl,
                model_name,
                basedate_since.strftime("%s"),
                end_date.strftime("%s")
            )
            if from_id is not None:
                info_url += "&from_id={}".format(from_id)

            r = rs.get(info_url).json()[model_name]
            total_updates = r['count']

            if from_id is None:  # First round baby
                nb_steps_total = math.ceil(total_updates/chunk_size)
                # update the end_date for filename consistency
                # latest_update_date = datetime.datetime.strptime(r['latest_update'], '%Y-%m-%dT%H:%M:%S.%f').strftime('%s')

        except Exception as e:
            print(e)
            res.update({"status": "error"})
            dsj.status = 'failed'
            dsj.save()
            return res

        # Exit loop if no updates available
        if total_updates == 0:
            break

        # If there is too much results, import the first onces then store the last_id for the next iteration as from_id
        from_id = r['oldest_id']

        # Create a DataSync entry
        ds = DataSync.objects.create(
            job=dsj,
            since_date=basedate_since,
            # to_date=end_date,  # has to be set when results arrives
            mdl_name=model_name,
            from_id=from_id,
            comments="URL: {}\nTOKEN: {}\n".format(
                settings.HEARS_DATASYNC_URL,
                settings.HEARS_DATASYNC_AUTHTOKEN[:6]+"*******"
            )
        )

        # Download sync entries for the day lap
        try:
            getdata_url = "{}/api/data/export/model?model={}&since={}&to={}&chunk_size={}&from_id={}&stream=1".format(
                baseurl,
                model_name,
                basedate_since.strftime("%s"),
                end_date.strftime("%s"),
                chunk_size,
                from_id
            )
            # print(getdata_url)
            import_data = rs.get(getdata_url)
            import_data_dict = json.loads(import_data.content)

            # https://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
            # Store the tmp file to disk
            import_fp = 'media/data/import/updates_{}_{}_{}_{}.json'.format(
                model_name,
                from_id,
                basedate_since.strftime('%s'),
                # latest_update_date,
                import_data_dict['last_update_epoch']
            )
            if store is True:
                open(import_fp, 'wb').write(import_data.content)

        except Exception as e:
            print(e)
            res.update({"status": "error"})
            ds.status = 'failed'
            ds.comments += 'Error when downloading sync file from referential.\n{}'.format(e)
            ds.save()
            dsj.status = 'failed'
            dsj.save()
            break

        # Update the from_id (last_id from data downloaded)
        from_id = int(import_data_dict['last_id'])

        # if count < chunk_size: no more updates should be available
        if import_data_dict['count'] < chunk_size:
            has_more_updates = False

        # Import data
        try:
            import_data_res = _import_data(import_data_dict)
        except Exception as e:
            print(e)
            res.update({"status": "error"})
            ds.status = 'failed'
            ds.comments += 'Error when importing sync file from referential.\n{}'.format(e)
            ds.save()
            dsj.status = 'failed'
            dsj.save()
            break

        # print(import_data_res)

        if len(import_data_res['errors']) == 0:
            ds.has_more_updates = has_more_updates
            ds.to_date = import_data_dict['last_update']
            ds.status = 'finished'
            ds.save()
        else:
            # print(import_data_res['errors'])
            ds.status = 'failed'
            ds.comments += 'Errors appears when importing updates.\n'
            ds.save()
            dsj.status = 'failed'
            dsj.save()
            break

        # Show progression
        nb_steps_done += 1
        dsj.progression = (nb_steps_done/nb_steps_total)*100
        dsj.save()
        print("Update progress for '{}': {:.2f}%".format(model_name, (nb_steps_done/nb_steps_total)*100))

    dsj.status = 'finished'
    dsj.save()

    return res


'''
Steps
- check local last sync
if null (no datasync): take date from the last created object
- pull data info from the remote hears instance
- for each day:
  + create a datasync entry
  + download export data dump to a tmp file
      For each table, start from last entry to first. Break when entry is already inserted
  + update data from the tmp file
  + update datasync (status=finished)
'''
def _run_datasync(limit, since=None, to=None):
    res = {}

    last_valid_datasync = DataSync.objects.filter(status='finished').order_by('-to_date').first()

    if last_valid_datasync is None:
        eai = _export_data_info(since=datetime.datetime.strptime(settings.HEARS_DATASYNC_BASEDATE, '%Y-%m-%d').strftime('%s'))
        basedate_since = eai['latest_update']
    else:
        basedate_since = last_valid_datasync.to_date

    end_date = datetime.datetime.today()
    if to is not None:
        try:
            end_date = datetime.datetime.fromtimestamp(int(to))
        except Exception:
            res.update({"status": "error", "reason": "bad format for parameter 'to'. Expecting '%s' (Unix epoch format)"})
            return res

    # Initialize requests session
    baseurl = settings.HEARS_DATASYNC_URL
    rs = requests.Session()
    rs.headers['Authorization'] = 'Token {}'.format(settings.HEARS_DATASYNC_AUTHTOKEN)
    rs.proxies = settings.PROXIES
    rs.verify = settings.HEARS_DATASYNC_SSLVERIFY
    rs.timeout = settings.HEARS_DATASYNC_TIMEOUT

    has_more_updates = True

    # Loop over updates and sync !
    while has_more_updates:
        try:
            r = rs.get("{}/api/data/export/info?since={}".format(baseurl, basedate_since.strftime("%s"))).json()
            total = r['total']
            oldest_update_str = r['oldest_update']
            oldest_update = datetime.datetime.strptime(oldest_update_str, '%Y-%m-%dT%H:%M:%S.%f')
        except Exception as e:
            res.update({"status": "error", "reason": e.message})
            return res
        #
        # print("total:", total)
        # print("oldest_update:", oldest_update)
        # print("end_date:", end_date)

        # Exit loop when the oldest update is after the end_date
        if oldest_update > end_date:
            has_more_updates = False

        if total == 0:
            continue

        # Update basedate when the oldest update is after
        if basedate_since < oldest_update:
            basedate_since = oldest_update

        sync_date_next = basedate_since + datetime.timedelta(days=1)

        # Create a DataSync entry
        ds = DataSync.objects.create(
            since_date=basedate_since,
            to_date=sync_date_next,
            comments="URL: {}\nTOKEN: {}\n".format(
                settings.HEARS_DATASYNC_URL,
                settings.HEARS_DATASYNC_AUTHTOKEN[:6]+"*******"
            )
        )

        # Download sync entries for the day lap
        try:
            import_data_day = rs.get("{}/api/data/export/full?since={}&to={}&stream=1&limit={}".format(
                baseurl,
                basedate_since.strftime('%s'),
                sync_date_next.strftime('%s'),
                limit
                )
            )

            import_data_day_dict = json.loads(import_data_day.content)

            # https://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
            import_fp = 'media/data/import/updates_{}_{}_{}.json'.format(
                basedate_since.strftime('%s'),
                sync_date_next.strftime('%s'),
                import_data_day_dict['last_update_epoch']
            )
            open(import_fp, 'wb').write(import_data_day.content)

        except Exception as e:
            res.update({"status": "error"})
            ds.status = 'error'
            ds.comments += 'Error when downloading sync file from referential.\n{}'.format(e)
            ds.save()
            break

        # Import data
        try:
            import_data_res = _import_data(import_data_day_dict)
        except Exception as e:
            res.update({"status": "error"})
            ds.status = 'error'
            ds.comments += 'Error when importing sync file from referential.\n{}'.format(e)
            ds.save()
            break

        if len(import_data_res['errors']) == 0:
            ds.status = 'finished'
            ds.save()
        else:
            ds.status = 'error'
            ds.comments += 'Errors appears when importing updates.\n{}'.format(e)
            ds.save()
            break
        basedate_since = sync_date_next

    return res
