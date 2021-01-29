from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.conf import settings
from django.apps import apps
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from users.permissions import AllowDataSync
from common.utils import _json_serial
from common.utils.constants import DATASYNC_MODELS
from vulns.models import Vuln, ExploitMetadata, ThreatMetadata
from .utils import (
    _export_data_info_model, _export_data_model,
    _export_data_info, _export_data,
    _import_data,
    _run_datasync_model,
    # _run_datasync
)
from .tasks import run_datasync_task, run_datasync_model_task, run_datasync_models_task
from .models import DataSync

from io import BytesIO
from zipfile import ZipFile
import datetime
import json
import os
import logging
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def submit_metadata(self):
    submission = self.data.dict().copy()

    vuln = None
    link_type = "exploit"

    # First, search with the CVE ID
    if 'cveid' in submission.keys():
        vuln = Vuln.objects.filter(cveid=submission['cveid']).first()
        submission.pop('cveid', None)

    # Otherwise, check if a vuln ID is given
    if vuln is None and 'vuln_id' in submission.keys():
        vuln = Vuln.objects.filter(id=submission['vuln_id']).first()
        submission.pop('vuln_id', None)

    if vuln is None:
        return JsonResponse({
            "status": "error",
            "message": "Unable to find vuln"
            }, safe=False)

    if 'submit_type' in submission.keys() and submission['submit_type'] in ['exploit', 'threat']:
        link_type = submission['submit_type']
    else:
        link_type = "exploit"

    submission.pop('submit_type', None)
    submission.update({'vuln_id': str(vuln.id)})

    s = None
    if link_type == 'exploit':
        try:
            for sl in vuln.exploitmetadata_set.values_list('link', flat=True):
                if submission['link'].rstrip('/') in sl.rstrip('/'):
                    return JsonResponse({
                        "status": "error",
                        "message": "Exploit already related to vulnerability"
                        }, safe=False)
                s = ExploitMetadata(**submission)
        except Exception as e:
            print(e)
            return JsonResponse({
                "status": "error",
                "message": "Something goes wrong on ExploitMetadata creation"
                }, safe=False)
    elif link_type == 'threat':
        try:
            for sl in vuln.threatmetadata_set.values_list('link', flat=True):
                if submission['link'].rstrip('/') in sl.rstrip('/'):
                    return JsonResponse({
                        "status": "error",
                        "message": "Threat news already related to vulnerability"
                        }, safe=False)
                s = ThreatMetadata(**submission)
        except Exception as e:
            print(e)
            return JsonResponse({
                "status": "error",
                "message": "Something goes wrong on ThreatMetadata creation"
                }, safe=False)

    s.save()

    return JsonResponse({"status": "submitted", "type": link_type, "id": s.id}, safe=False)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def import_vulns(self):
    data = self.data.copy()

    if 'vulns' in data.keys():
        for vuln in data['vulns']:
            vuln.pop('id', None)
            try:
                v = Vuln.objects.filter(uuid=vuln['uuid']).first()
                new_vuln = None
                if v is None:
                    # New vuln
                    new_vuln = Vuln(**vuln)
                    new_vuln.save()
                else:
                    v.update(**vuln)
            except Exception as e:
                logger.error(e)

    if 'exploits' in data.keys():
        for exploit in data['exploits']:
            exploit.pop('id', None)
            try:
                v = Vuln.objects.filter(uuid=exploit['vuln_uuid']).first()
                exploit.update({'vuln_id': v.id})
                new_exploit = ExploitMetadata(**exploit)
                new_exploit.save()
            except Exception as e:
                logger.error(e)

    return JsonResponse({}, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser, AllowDataSync])
def export_latest_vulns(self):
    MAX_VULNS = int(self.GET.get('limit', 100))
    export_format = self.GET.get('type', 'json')
    export_since = self.GET.get('since', datetime.datetime.now() - datetime.timedelta(days=1))
    if not isinstance(export_since, datetime.date):
        try:
            export_since = datetime.datetime.strptime(export_since, '%Y-%M-%d').date()
        except Exception:
            return JsonResponse({
                "status": "error",
                "message": "'since' parameter is invalid. Use '%Y-%M-%d'"},
                safe=False)

    export_to = self.GET.get('to', datetime.datetime.now())
    if not isinstance(export_to, datetime.date):
        try:
            export_to = datetime.datetime.strptime(export_to, '%Y-%M-%d').date()
        except Exception:
            return JsonResponse({
                "status": "error",
                "message": "'to' parameter is invalid. Use '%Y-%M-%d'"},
                safe=False)
    with_exploits = self.GET.get('with_exploits', True)
    with_threats = self.GET.get('with_threats', True)
    # with_timeline = self.GET.get('with_timeline', True)
    exp_filename = "patrowlhears_exp_vulns_{}".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3])

    vulns = []
    exploits = []
    threats = []
    for vuln in Vuln.objects.filter(created_at__gte=export_since, updated_at__lte=export_to)[:MAX_VULNS]:
        vulns.append(vuln.to_dict())

        if with_exploits is True:
            for exploit in vuln.exploitmetadata_set.all():
                exploits.append(exploit.to_dict())

        if with_threats is True:
            for threat in vuln.threatmetadata_set.all():
                threats.append(threat.to_dict())

    export_data = {
        'vulns': vulns,
        'exploits': exploits,
        'threats': threats,
    }

    if export_format == "zip":
        in_memory = BytesIO()
        zip = ZipFile(in_memory, "a")
        zip.writestr("all.json", json.dumps(export_data, sort_keys=True, default=_json_serial))
        zip.writestr("vulns.json", json.dumps({'vulns': vulns}, sort_keys=True, default=_json_serial))
        zip.writestr("exploits.json", json.dumps({'exploits': exploits}, sort_keys=True, default=_json_serial))
        zip.writestr("threats.json", json.dumps({'threats': threats}, sort_keys=True, default=_json_serial))

        # fix for Linux zip files read in Windows
        for file in zip.filelist:
            file.create_system = 0

        zip.close()

        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename={}.zip".format(exp_filename)

        in_memory.seek(0)
        response.write(in_memory.read())
        return response
    else:
        return JsonResponse(export_data, safe=False)


@api_view(['GET'])
@permission_classes((AllowDataSync,))
def export_data_info(self):
    """
    Get updates info per model.
    """
    model_name = self.GET.get('model', None)
    if model_name is not None and model_name in DATASYNC_MODELS.keys():
        data = _export_data_info_model(
            model_class=apps.get_model(DATASYNC_MODELS[model_name]),
            model_name=model_name,
            since=self.GET.get('since', None),
            to=self.GET.get('to', None),
            from_id=self.GET.get('from_id', None)
        )
    else:
        data = _export_data_info(
            since=self.GET.get('since', None),
            to=self.GET.get('to', None)
        )
    return JsonResponse(data, safe=False)


@api_view(['GET'])
@permission_classes((AllowDataSync,))
def export_data_model(self):
    """
    Get updates per model.
    Streamed response on-demand
    """
    model_name = self.GET.get('model', None)
    if model_name is None or model_name not in DATASYNC_MODELS.keys():
        return JsonResponse({
            "status": "error",
            "reason": "bad model name '{}'".format(model_name)}
            , safe=False)

    data = _export_data_model(
        model_class=apps.get_model(DATASYNC_MODELS[model_name]),
        model_name=model_name,
        since=self.GET.get('since', None),
        to=self.GET.get('to', None),
        from_id=self.GET.get('from_id', None),
        chunk_size=self.GET.get('chunk_size', None),
    )

    if self.GET.get('stream', None) is not None:
        # Save data to local file
        data_export = json.dumps(data, default=_json_serial)
        export_filename = 'updates_{}_{}_{}_{}.json'.format(
            model_name,
            data['export_since'].strftime('%s'),
            data['export_to'].strftime('%s'),
            data['last_update'].strftime('%s')
        )

        # Prepare and serve response
        response = StreamingHttpResponse(
            data_export,
            status=200,
            content_type='application/octet-stream')
        response['Cache-Control'] = 'no-cache'
        response['Content-Disposition'] = 'attachment; filename={};'.format(export_filename)
        return response

    return JsonResponse(data, safe=False)


@api_view(['GET'])
@permission_classes((AllowDataSync,))
def export_data_full(self):

    # @todo: use cache (already existing files)
    # @todo: serve ZIP file as StreamingHttpResponse

    data = _export_data(
        limit=int(self.GET.get('limit', 999999999)),
        since=self.GET.get('since', None),
        to=self.GET.get('to', None)
    )

    if self.GET.get('stream', None) is not None:
        # Save data to local file
        data_export = json.dumps(data, default=_json_serial)
        export_filename = 'updates_{}_{}_{}.json'.format(
            data['export_since'].strftime('%s'),
            data['export_to'].strftime('%s'),
            data['last_update'].strftime('%s')
        )

        # Check if a dump already exists, otherwise create it
        export_fp = 'media/data/export/{}'.format(export_filename)
        if os.path.isfile(export_fp) is False:
            with open(export_fp, 'w', encoding="utf8") as f:
                f.write(data_export)

        # Prepare and serve response
        response = StreamingHttpResponse(
            open('media/data/export/{}'.format(export_filename)),
            status=200,
            content_type='application/octet-stream')
        response['Cache-Control'] = 'no-cache'
        response['Content-Disposition'] = 'attachment; filename={};'.format(export_filename)
        return response

    if self.GET.get('f', '').lower() == 'zip':
        exp_filename = "patrowlhears_datadump_{}".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3])
        in_memory = BytesIO()
        zip = ZipFile(in_memory, "a")
        zip.writestr("all.json", json.dumps(data, sort_keys=True, default=_json_serial))
        zip.writestr("vulns.json", json.dumps({'vulns': data['vulns']}, sort_keys=True, default=_json_serial))
        zip.writestr("exploits.json", json.dumps({'exploits': data['exploits']}, sort_keys=True, default=_json_serial))
        zip.writestr("threats.json", json.dumps({'threats': data['threats']}, sort_keys=True, default=_json_serial))
        zip.writestr("kb_cwe.json", json.dumps({'kb_cwe': data['kb_cwe']}, sort_keys=True, default=_json_serial))
        zip.writestr("kb_cpe.json", json.dumps({'kb_cpe': data['kb_cpe']}, sort_keys=True, default=_json_serial))
        zip.writestr("kb_cve.json", json.dumps({'kb_cve': data['kb_cve']}, sort_keys=True, default=_json_serial))
        zip.writestr("kb_vendor.json", json.dumps({'kb_vendor': data['kb_vendor']}, sort_keys=True, default=_json_serial))
        zip.writestr("kb_product.json", json.dumps({'kb_product': data['kb_product']}, sort_keys=True, default=_json_serial))
        zip.writestr("kb_product_version.json", json.dumps({'kb_product_version': data['kb_product_version']}, sort_keys=True, default=_json_serial))

        # fix for Linux zip files read in Windows
        for file in zip.filelist:
            file.create_system = 0

        zip.close()

        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename={}.zip".format(exp_filename)

        in_memory.seek(0)
        response.write(in_memory.read())
        return response
    else:
        return JsonResponse(data, safe=False)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def import_data(self):
    data = self.data.copy()
    status, results = _import_data(data)

    return JsonResponse({"status": status, "results": results}, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_last_datasync(self):
    res = {}

    last_valid_datasync = DataSync.objects.filter(status='finished').order_by('-to_date').first()
    if last_valid_datasync is not None:
        res = last_valid_datasync.to_dict()

    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_datasync_info(self):
    # Todo: create a celery task
    lvd = None
    last_valid_datasync = DataSync.objects.filter(status='finished').order_by('-to_date').first()
    if last_valid_datasync is not None:
        lvd = last_valid_datasync.to_dict()

    data = {
        "mode": settings.HEARS_DATASYNC_MODE,
        "url": settings.HEARS_DATASYNC_URL,
        "authtoken": settings.HEARS_DATASYNC_AUTHTOKEN[:6]+"*******",
        "frequency": settings.HEARS_DATASYNC_FREQUENCY,
        "is_enabled": settings.HEARS_DATASYNC_ENABLED,
        "basedate": settings.HEARS_DATASYNC_BASEDATE,
        "last_valid_datasync": lvd
    }
    return JsonResponse(data, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def run_datasync(self):
    model_name = self.GET.get('model', None)
    store = self.GET.get('store', 'true').lower() in ['true', 'yes', 1, 'y', 'on']
    if model_name is not None and model_name not in DATASYNC_MODELS.keys():
        return JsonResponse({
            "status": "error",
            "reason": "bad model name '{}'. Allowed model names are: {}".format(
                model_name,
                ", ".join([m for m in DATASYNC_MODELS.keys()])
            )
        }, safe=False)

    if model_name is not None and model_name in DATASYNC_MODELS.keys():
        data = _run_datasync_model(
            model_class=apps.get_model(DATASYNC_MODELS[model_name]),
            model_name=model_name,
            # since=self.GET.get('since', None),
            # to=self.GET.get('to', None),
            # from_id=self.GET.get('from_id', None),
            chunk_size=self.GET.get('chunk_size', None),
            store=store
        )
    else:
        # Otherwise sync all tables !
        for model_name in DATASYNC_MODELS.keys():
            _run_datasync_model(
                model_class=apps.get_model(DATASYNC_MODELS[model_name]),
                model_name=model_name,
                chunk_size=self.GET.get('chunk_size', None),
                store=store
            )
    return JsonResponse(data, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def run_datasync_async(self):
    # Todo: create a celery task
    run_datasync_task.apply_async(
        args=[
            int(self.GET.get('limit', 9999999)),
            self.GET.get('since', None),
            self.GET.get('to', None)
            ],
        queue='default',
        retry=False
    )
    return JsonResponse({"status": "enqueued"}, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def run_datasync_models_async(self):
    model_name = self.GET.get('model', None)
    # store = self.GET.get('store', 'true').lower() in ['true', 'yes', '1', 'y', 'on']
    if model_name is not None and model_name not in DATASYNC_MODELS.keys():
        return JsonResponse({
            "status": "error",
            "reason": "bad model name '{}'. Allowed model names are: {}".format(
                model_name,
                ", ".join([m for m in DATASYNC_MODELS.keys()])
            )
        }, safe=False)

    if model_name is not None and model_name in DATASYNC_MODELS.keys():
        run_datasync_model_task.apply_async(
            args=[
                model_name,
                int(self.GET.get('limit', 9999999)),
                self.GET.get('since', None),
                self.GET.get('to', None),
                self.GET.get('store', 'true').lower() in ['true', 'yes', '1', 'y', 'on']
            ],
            queue='default',
            retry=False
        )
    else:
        run_datasync_models_task.apply_async(
            args=[
                int(self.GET.get('limit', 9999999)),
                self.GET.get('since', None),
                self.GET.get('to', None),
                self.GET.get('store', 'true').lower() in ['true', 'yes', '1', 'y', 'on']
            ],
            queue='default',
            retry=False
        )
    return JsonResponse({"status": "enqueued"}, safe=False)
