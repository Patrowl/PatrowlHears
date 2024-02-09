from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.db.models import F, Value, Case, BooleanField, When, CharField, Count, Q
from common.utils.pagination import StandardResultsSetPagination
from common.utils import organization, get_api_default_permissions, _json_serial
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from users.permissions import AllowManageMetadata
from cves.models import Product, Vendor, ProductVersion, Package, CVE, CWE, CPE
from alerts.tasks import slack_alert_vuln_task, send_email_message_task
from .models import (
    Vuln, ExploitMetadata, ThreatMetadata,
    OrgExploitMetadata, OrgThreatMetadata, OrgVulnMetadata
)
from .serializers import (
    VulnSerializer, VulnFilter,
    ExploitMetadataSerializer, ExploitMetadataFilter,
    ThreatMetadataSerializer, ThreatMetadataFilter,
    OrgExploitMetadataSerializer, OrgExploitMetadataFilter,
    OrgThreatMetadataSerializer, OrgThreatMetadataFilter
)
from .tasks import (
    refresh_vulns_score_task, refresh_vulns_product_versions_task,
    email_daily_report_task, email_weekly_report_task, email_monthly_report_task
)

from cpe import CPE as _CPE
from datetime import datetime, timedelta
import uuid
import json


class VulnSet(viewsets.ModelViewSet):
    """API endpoint that allows vuln to be viewed or edited."""

    serializer_class = VulnSerializer
    filterset_class = VulnFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination
    # filter_fields = ('exploit_count', )

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=self.request.user, org_id=org_id)
        monitored_vulns = []
        if org is not None:
            monitored_vulns = org.org_monitoring_list.vulns.all().only('id')
        qs = Vuln.objects.all().select_related('cwe').prefetch_related(
            'exploitmetadata_set', 'orgexploitmetadata_set',
            'products', 'products__vendor', 'productversions'
        ).annotate(
            exploit_count=F('id'),
            monitored=Count("id", filter=Q(id__in=monitored_vulns)),
            org=Value(org_id, output_field=CharField())
        ).order_by('-updated_at')

        return qs


class ExploitMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows exploit metadata to be viewed or edited."""

    queryset = ExploitMetadata.objects.prefetch_related(
        'vuln__products', 'vuln__products__vendor'
    ).select_related(
        'vuln'
    ).annotate(
        vp=F('vuln__vulnerable_products')
    ).order_by('-updated_at')
    serializer_class = ExploitMetadataSerializer
    filterset_class = ExploitMetadataFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)


class OrgExploitMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows Org exploit metadata to be viewed or edited."""

    serializer_class = OrgExploitMetadataSerializer
    filterset_class = OrgExploitMetadataFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=self.request.user, org_id=org_id)
        if org is None:
            return None

        return OrgExploitMetadata.objects.prefetch_related('vuln').annotate(
            vp=F('vuln__vulnerable_products')
        ).filter(organization=org).order_by('-updated_at')


class ThreatMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows threat metadata to be viewed or edited."""

    queryset = ThreatMetadata.objects.prefetch_related('vuln').annotate(
        vp=F('vuln__vulnerable_products')
    ).order_by('-updated_at')
    serializer_class = ThreatMetadataSerializer
    filterset_class = ThreatMetadataFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)


class OrgThreatMetadataSet(viewsets.ModelViewSet):
    """API endpoint that allows Org Threat metadata to be viewed or edited."""

    serializer_class = OrgThreatMetadataSerializer
    filterset_class = OrgThreatMetadataFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        return get_api_default_permissions(self)

    def get_queryset(self):
        org_id = self.request.session.get('org_id', None)
        org = organization.get_current_organization(user=self.request.user, org_id=org_id)
        if org is None:
            return None

        return OrgThreatMetadata.objects.prefetch_related('vuln').annotate(
            vp=F('vuln__vulnerable_products')
        ).filter(organization=org).order_by('-updated_at')


HISTORY_IMPORTANT_FIELDS = {
    'vuln': [
        'cvss', 'cvss_vector',
        'cvss3', 'cvss3_vector',
        'summary', 'is_exploitable', 'is_confirmed',
        'is_in_the_news', 'is_in_the_wild'
    ],
    'exploit': [
        'link', 'trust_level', 'tlp_level', 'source', 'availability',
        'maturity'
    ],
    'threat': [
        'link', 'trust_level', 'tlp_level', 'source', 'is_in_the_news',
        'is_in_the_news'
    ]
}


def get_history_diffs(item, scope):
    diffs = {}

    record = item.history.earliest()
    diffs.update({
        record.history_date.timestamp(): {
            'date': record.history_date,
            'reason': 'New {} created'.format(scope),
            'changes': ["'{}' has been set to '{}'".format(f, getattr(record, f)) for f in HISTORY_IMPORTANT_FIELDS[scope]],
            'scope': scope
        }
    })
    while True:
        hdiffs = []
        next = record.next_record
        if next is None:
            break
        delta = next.diff_against(record)
        for change in delta.changes:
            hdiffs.append("'{}' changed from '{}' to '{}'".format(change.field, change.old, change.new))
        if len(hdiffs) > 0:
            diffs.update({
                next.history_date.timestamp(): {
                    'date': next.history_date,
                    'reason': 'Change in {}'.format(scope),
                    'changes': hdiffs,
                    'scope': scope
                }
            })
        record = next

    return diffs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vuln_history(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse({"status": "error", "reason": "unable to get the organization"}, safe=False, status=500)
    res = {}

    res.update(get_history_diffs(vuln, 'vuln'))

    for exploit in vuln.exploitmetadata_set.all():
        res.update(get_history_diffs(exploit, 'exploit'))
    for exploit in vuln.orgexploitmetadata_set.filter(organization=org):
        res.update(get_history_diffs(exploit, 'exploit'))
    for threat in vuln.threatmetadata_set.all():
        res.update(get_history_diffs(threat, 'threat'))
    for threat in vuln.orgthreatmetadata_set.filter(organization=org):
        res.update(get_history_diffs(threat, 'threat'))
    history = []
    for h in sorted(res.keys()):
        history.append(res[h])
    return JsonResponse(history, safe=False)


@api_view(['POST'])
@permission_classes([AllowManageMetadata])
def add_vuln(self):
    res = {"status": "success", "reason": "vulnerability successfully created"}
    # print(self.data)

    cve_data = {
        "cve_id": self.data['cve_id'],
        "summary": self.data.get('summary', 'n/a'),
        "published": self.data.get('published', datetime.today()),
        "modified": self.data.get('modified', datetime.today()),
        "cwe": CWE.objects.filter(cwe_id=self.data.get('cwe', '')).first(),
        "cvss_time": self.data.get('cvss_time', datetime.today()),
        "cvss_vector": self.data.get('cvss2_vector', ''),
        "cvss3_vector": self.data.get('cvss3_vector', ''),
        "access": {
            "authentication": self.data.get('access_authentication', ''),
            "complexity": self.data.get('access_complexity', ''),
            "vector": self.data.get('access_vector', ''),
        },
        "impact": {
            "confidentiality": self.data.get('impact_confidentiality', ''),
            "integrity": self.data.get('impact_integrity', ''),
            "availability": self.data.get('impact_availability', ''),
        },
        "references": {
            "others": []
        },
        "assigner": self.user.username,
        "vulnerable_products": []
    }
    if CVE.objects.filter(cve_id=cve_data["cve_id"]).count() > 0:
        res = {"status": "error", "reason": "CVE already known."}
        return JsonResponse(res, safe=False)

    # Check CVSSv2
    cvss2_data = self.data.get('cvss2', None)
    cvss2 = 0.0
    try:
        if cvss2_data is not None and cvss2_data != '':
            cvss2 = float(cvss2_data)
    except Exception:
        pass
    cve_data.update({"cvss": cvss2})

    # Check CVSSv3
    cvss3_data = self.data.get('cvss3', None)
    cvss3 = 0.0
    try:
        if cvss3_data is not None and cvss3_data != '':
            cvss3 = float(cvss3_data)
    except Exception:
        pass
    cve_data.update({"cvss3": cvss3})

    # Sanitize
    if type(cve_data['published']) != datetime:
        cve_data['published'] = datetime.today()

    if 'references' in self.data.keys() and len(self.data['references']) > 0:
        cve_data["references"]["others"] = [r.strip() for r in self.data['references'].replace('\n', ',').split(',')]

    # Create a CVE
    cve = CVE(**cve_data)
    try:
        cve.full_clean()
        cve.save()
    except Exception:
        res = {"status": "error", "reason": "Unable to create CVE in DB"}
        return JsonResponse(res, safe=False)

    # Manage CPEs and related products
    vulnerable_products = []  # Array
    products = []  # List of Product
    productversions = []  # List of ProductVersion

    # -> Loop over products
    if 'products' in self.data.keys() and len(self.data['products']) > 0:
        for pid in self.data['products']:
            p = Product.objects.filter(id=pid).first()
            if p is not None and p not in products:
                products.append(p)

    # Loop over CPEs
    if 'cpes' in self.data.keys() and len(self.data['cpes']) > 0:
        cpes = [c.strip() for c in self.data['cpes'].replace('\n', ',').split(',')]

        my_cpes = list(CPE.objects.values_list('vector', flat=True))
        for cpe in cpes:
            if cpe == '':
                continue
            try:
                c = _CPE(cpe)
                vendor, is_new_vendor = Vendor.objects.get_or_create(name=c.get_vendor()[0])
                product, is_new_product = Product.objects.get_or_create(name=c.get_product()[0], vendor=vendor)
                productversion, is_new_productversion = ProductVersion.objects.get_or_create(version=c.get_version()[0], product=product, vector=cpe)

                if cpe not in vulnerable_products:
                    vulnerable_products.append(cpe)
                if product not in products:
                    products.append(product)
                if productversion not in productversions:
                    productversions.append(productversion)

                if cpe not in my_cpes:
                    new_cpe = CPE(
                        vector=cpe,
                        title=cpe,
                        vendor=vendor,
                        product=product,
                        vulnerable_products=[]
                    )
                    new_cpe.save()

                    # Add the current CPE to inner list
                    my_cpes.append(cpe)
            except Exception:
                pass

    cve.vulnerable_products = list(set(vulnerable_products))  # Deduplicate
    for p in products:
        cve.products.add(p)
    for pv in productversions:
        cve.productversions.add(pv)
    cve.save()

    # Create a Vuln
    vuln_data = dict(cve_data)
    vuln_data.pop("references")
    vuln_data["reflinks"] = cve_data["references"]["others"]
    vuln_data["cve_id"] = cve.id
    vuln_data["vulnerable_products"] = cve.vulnerable_products
    vuln_data["cveid"] = cve.cve_id
    vuln_data["uuid"] = uuid.uuid4()
    vuln_data["reflinkids"] = dict()
    vuln_data["is_exploitable"] = str(self.data.get('is_exploitable', 'false')).lower() in ['true', 'yes', 'y', 'on', '1']
    vuln_data["is_confirmed"] = str(self.data.get('is_confirmed', 'false')).lower() in ['true', 'yes', 'y', 'on', '1']
    vuln_data["is_in_the_news"] = str(self.data.get('is_in_the_news', 'false')).lower() in ['true', 'yes', 'y', 'on', '1']
    vuln_data["is_in_the_wild"] = str(self.data.get('is_in_the_wild', 'false')).lower() in ['true', 'yes', 'y', 'on', '1']

    vuln = Vuln(**vuln_data)
    try:
        vuln.full_clean()
        vuln.save()
    except Exception:
        cve.delete()
        res = {"status": "error", "reason": "Unable to create vulnerability in DB"}
        return JsonResponse(res, safe=False)

    # Update products and productversion lists
    for p in products:
        vuln.products.add(p)
    for pv in productversions:
        vuln.productversions.add(pv)
    vuln.update_product_versions()
    vuln.save()

    # Check if the vulnerability is monitored
    monitored = False
    if 'monitored' in self.data.keys() and type(self.data['monitored']) == bool:
        monitored = self.data['monitored']
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
        if org is not None and monitored is True and vuln not in org.org_monitoring_list.vulns.all():
            org.org_monitoring_list.vulns.add(vuln)

    res.update({"data": vuln.to_dict()})

    return JsonResponse(res, safe=False)


@api_view(['POST'])
@permission_classes([AllowManageMetadata])
def edit_vuln(self):
    res = {"status": "error", "reason": "not yet implemented"}
    # print(self.data)
    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vuln_cpes(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    return JsonResponse({'cpes': vuln.vulnerable_products}, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_vuln_json(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse({
            "status": "error",
            "reason": "Unable to get the organization"}, safe=False, status=500)

    # Set default values
    vuln.org = self.session.get('org_id', None)
    vuln.monitored = False
    vuln.exploit_count = 1
    vuln_json = VulnSerializer(vuln, context={'request': self}).data
    exploits_json = ExploitMetadataSerializer(vuln.exploitmetadata_set.all(), many=True, context={'request': self}).data
    orgexploits_json = OrgExploitMetadataSerializer(vuln.orgexploitmetadata_set.filter(organization=org), many=True, context={'request': self}).data
    threats_json = ThreatMetadataSerializer(vuln.threatmetadata_set.all(), many=True, context={'request': self}).data
    orgthreats_json = OrgThreatMetadataSerializer(vuln.orgthreatmetadata_set.filter(organization=org), many=True, context={'request': self}).data

    res_json = {
        "vulnerability": vuln_json,
        "exploits": exploits_json,
        "org_exploits": orgexploits_json,
        "threats": threats_json,
        "org_threats": orgthreats_json,
    }

    response = HttpResponse(json.dumps(res_json, sort_keys=True, indent=4, default=_json_serial), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=hears_vuln_{}.json'.format(vuln.id)
    return response


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def export_vuln_sendmail(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    emails = self.data.get('emails', None)
    if emails is not None:
        emails = " ".join(emails.split()).replace(' ', '').replace(';', ',').replace(' ', ',').split(',')[:10]
        try:
            send_email_message_task.apply_async(
                args=[
                    "[PatrowlHears] PH-{} / Vulnerability details".format(vuln.id),
                    vuln.to_dict(),
                    'vuln',
                    emails
                ],
                queue='alerts',
                retry=False
            )
            return JsonResponse({"status": "success"}, safe=False)
        except Exception as e:
            print(e)
            pass
    return JsonResponse({
        "status": "error",
        "reason": "No valid email provided"}, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_number_exploits_threats(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse({
            "status": "error",
            "reason": "Unable to get the organization"}, safe=False, status=500)

    # Get exploits
    len_exploits = len(vuln.exploitmetadata_set.all())
    # Get org exploits
    len_org_exploits = len(vuln.orgexploitmetadata_set.filter(organization=org))
    # Count exploits
    exploit_count = len_exploits + len_org_exploits

    # Get public threats
    len_threats = len(vuln.threatmetadata_set.all())
    # Get org threats
    len_org_threats = len(vuln.orgthreatmetadata_set.filter(organization=org))
    # Count threats
    threat_count = len_org_threats + len_threats

    res = {
        "count_threat": threat_count,
        "count_exploit": exploit_count
    }

    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exploits(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse({
            "status": "error",
            "reason": "Unable to get the organization"}, safe=False, status=500)
    res = []

    # Get public exploits
    for exploit in vuln.exploitmetadata_set.all():
        e = model_to_dict(exploit)
        e['scope'] = 'public'
        e['relevancy_level'] = exploit.get_relevancy_level()
        res.append(e)

    # Get org exploits
    for exploit in vuln.orgexploitmetadata_set.filter(organization=org):
        e = model_to_dict(exploit)
        e['scope'] = 'private'
        e['relevancy_level'] = exploit.get_relevancy_level()
        res.append(e)
    return JsonResponse(res, safe=False)


@api_view(['POST'])
@permission_classes([AllowManageMetadata])
def add_exploit(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("Error: unable to get the organization", safe=False, status=500)

    data = {
        'vuln': vuln,
        'link': self.data['link'],
        'trust_level': self.data['trust_level'],
        'tlp_level': self.data['tlp_level'],
        'source': self.data['source'],
        'availability': self.data['availability'],
        'maturity': self.data['maturity'],
        'modified': self.data['modified'],
        'notes': self.data['notes'],
        'organization': org
    }
    new_exploit = OrgExploitMetadata(**data)
    new_exploit.save()
    # vuln.update_score(org=org)
    vuln.update_score()
    vuln.save()
    return JsonResponse(model_to_dict(new_exploit), safe=False)


@api_view(['POST'])
@permission_classes([AllowManageMetadata])
def edit_exploit(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    exploit = get_object_or_404(OrgExploitMetadata, id=self.data['id'])
    exploit.link = self.data['link']
    exploit.trust_level = self.data['trust_level']
    exploit.tlp_level = self.data['tlp_level']
    exploit.source = self.data['source']
    exploit.availability = self.data['availability']
    exploit.maturity = self.data['maturity']
    exploit.notes = self.data['notes']
    exploit.modified = self.data['modified']
    exploit.save()

    # Update vuln score
    vuln.update_score(org=org)
    vuln.save(org=org)

    return JsonResponse(model_to_dict(exploit), safe=False)


@api_view(['GET'])
@permission_classes([AllowManageMetadata])
def del_exploit(self, vuln_id, exploit_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    exploit = org.org_exploits.filter(id=exploit_id)
    if len(exploit) > 0:
        exploit.delete()
        vuln.update_score()
        vuln.save()
        return JsonResponse("deleted", safe=False)
    else:
        return JsonResponse("unknown", safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_threats(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)
    res = []

    # Get public threat
    for threat in vuln.threatmetadata_set.all():
        t = model_to_dict(threat)
        t['scope'] = 'public'
        res.append(t)

    # Get org threat
    for threat in vuln.orgthreatmetadata_set.filter(organization=org):
        t = model_to_dict(threat)
        t['scope'] = 'private'
        res.append(t)

    return JsonResponse(res, safe=False)


@api_view(['POST'])
@permission_classes([AllowManageMetadata])
def add_threat(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)
    data = {
        'vuln': vuln,
        'link': self.data['link'],
        'trust_level': self.data['trust_level'],
        'tlp_level': self.data['tlp_level'],
        'source': self.data['source'],
        'is_in_the_wild': self.data['is_in_the_wild'],
        'is_in_the_news': self.data['is_in_the_news'],
        'modified': self.data['modified'],
        'notes': self.data['notes'],
        'organization': org
    }
    new_threat = OrgThreatMetadata(**data)
    new_threat.save()

    # Update vuln score
    vuln.update_score()
    vuln.save()
    return JsonResponse(model_to_dict(new_threat), safe=False)


@api_view(['POST'])
@permission_classes([AllowManageMetadata])
def edit_threat(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    threat = get_object_or_404(OrgThreatMetadata, id=self.data['id'])
    threat.link = self.data['link']
    threat.is_in_the_wild = self.data['is_in_the_wild']
    threat.is_in_the_news = self.data['is_in_the_news']
    threat.trust_level = self.data['trust_level']
    threat.tlp_level = self.data['tlp_level']
    threat.source = self.data['source']
    threat.maturity = self.data['maturity']
    threat.notes = self.data['notes']
    threat.modified = self.data['modified']
    threat.save()

    # Update vuln score
    vuln.update_score()
    vuln.save()

    return JsonResponse(model_to_dict(threat), safe=False)


@api_view(['GET'])
@permission_classes([AllowManageMetadata])
def del_threat(self, vuln_id, threat_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse({"status": "error", "reason": "unable to get the organization"}, safe=False, status=500)

    threat = org.org_threats.filter(id=threat_id)
    threat.delete()

    # Update vuln score
    vuln.update_score()
    vuln.save()
    return JsonResponse("deleted", safe=False)


@api_view(['GET'])
@permission_classes([AllowManageMetadata])
def get_org_vuln_metadata(self, vuln_id):
    """Return dict with all org vuln metadata
    Args:
        vuln_id (str): The vuln id
    Returns:
        [dict]:
            - comment : str or '' if doesn't exist
            - status: undefined/fixed/not_interesting/in_progress or undefined if doesn't exist
    """
    # Check if the vulnerability exist
    vuln = get_object_or_404(Vuln, id=vuln_id)

    # Get the org object
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    # Find OrgVulnMetadata object with vuln and org. If doesn't exist return ""
    try:
        org_vuln_metadata = OrgVulnMetadata.objects.get(vuln=vuln, organization=org)
        return JsonResponse(
            {
                'comment': org_vuln_metadata.comment,
                'status': org_vuln_metadata.status
            }, safe=False)
    except ObjectDoesNotExist:
        pass

    return JsonResponse({'comment': "", 'status': 'undefined'}, safe=False)


@api_view(['GET'])
@permission_classes([AllowManageMetadata])
def get_org_vuln_comment(self, vuln_id):
    """Return comments linked to a vulnerability and an organization.

    Args:
        vuln_id (str): The vuln id
    Returns:
        [str]: The comment or "" if doesn't exist
    """
    # Check if the vulnerability exist
    vuln = get_object_or_404(Vuln, id=vuln_id)

    # Get the org object
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    # Find OrgVulnMetadata object with vuln and org. If doesn't exist return ""
    try:
        org_vuln_metadata = OrgVulnMetadata.objects.get(vuln=vuln, organization=org)
        return JsonResponse(org_vuln_metadata.comment, safe=False)
    except ObjectDoesNotExist:
        pass

    return JsonResponse("", safe=False)


@api_view(['POST'])
@permission_classes([AllowManageMetadata])
def edit_org_vuln_comment(self, vuln_id):
    """Update the comments linked to a vulnerability and an organization.

    Args:
        vuln_id (str): The vuln id
    Returns:
        [str]: the comment or an error
    """
    # Get the vulnerability object
    vuln = get_object_or_404(Vuln, id=vuln_id)

    # Get the organization return error if not found
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    # Verify comment in self.data. Create new OrgVulnData or Modify it.
    if 'comment' in self.data:
        comment = self.data['comment']
        try:
            org_vuln_metadata = OrgVulnMetadata.objects.get(vuln=vuln_id, organization=org.id)
            org_vuln_metadata.comment = self.data['comment']
            org_vuln_metadata.save()
        except ObjectDoesNotExist:
            # create a new OrgVulnMetadata object
            OrgVulnMetadata.objects.create(
                organization=org,
                vuln=vuln,
                comment=self.data['comment']
            )

        # return the comment
        return JsonResponse(comment, safe=False)

    return JsonResponse("error: invalid data", safe=False, status=500)


@api_view(['GET'])
@permission_classes([AllowManageMetadata])
def get_org_vuln_status(self, vuln_id):
    """Return a dict with the status
    Args:
        vuln_id (str): The vuln id
    Returns:
        [str]:
            - status: undefined/fixed/not_interesting/in_progress or undefined if doesn't exist
    """
    # Check if the vulnerability exist
    vuln = get_object_or_404(Vuln, id=vuln_id)

    # Get the org object
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    # Find OrgVulnMetadata object with vuln and org. If doesn't exist return "undefined"
    try:
        org_vuln_metadata = OrgVulnMetadata.objects.get(vuln=vuln, organization=org)
        return JsonResponse(org_vuln_metadata.status, safe=False)
    except ObjectDoesNotExist:
        pass

    return JsonResponse("undefined", safe=False)


@api_view(['POST'])
@permission_classes([AllowManageMetadata])
def edit_org_vuln_status(self, vuln_id):
    """ Modify the status linked to a vulnerability and an organization
    Args:
        vuln_id (str): The vuln id
    Returns:
        [str]: status undefined/fixed/not_interesting/in_progress or an error
    """

    STATUS_CHOICES = [
        'undefined', 'fixed',
        'not_interesting', "in_progress"
    ]

    # Get the vulnerability object
    vuln = get_object_or_404(Vuln, id=vuln_id)

    # Get the organization return error if not found
    try:
        org_id = self.session.get('org_id', None)
        org = organization.get_current_organization(user=self.user, org_id=org_id)
    except Exception:
        return JsonResponse("error: unable to get the organization", safe=False, status=500)

    # Verify status in self.data. Create new OrgVulnData or Modify it.
    if 'status' in self.data and self.data['status'] in STATUS_CHOICES:
        # Check if the vulnerability is monitored
        if vuln not in org.org_monitoring_list.vulns.all():
            return JsonResponse(
                "error: you can't modify status for a unmonitoring vulnerability",
                safe=False,
                status=500
            )

        status = self.data['status']
        try:
            org_vuln_metadata = OrgVulnMetadata.objects.get(vuln=vuln_id, organization=org.id)
            org_vuln_metadata.status = status
            org_vuln_metadata.save()
        except ObjectDoesNotExist:
            # create a new OrgVulnMetadata object
            OrgVulnMetadata.objects.create(
                organization=org,
                vuln=vuln,
                status=status
            )

        # return the comment
        return JsonResponse(status, safe=False)

    return JsonResponse("error: invalid data", safe=False, status=500)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def refresh_vuln_score(self, vuln_id):
    vuln = get_object_or_404(Vuln, id=vuln_id)
    vuln.update_score()
    vuln.save()
    return JsonResponse(vuln.score, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def refresh_vulns_score_async(self):
    refresh_vulns_score_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def refresh_vulns_product_versions_async(self):
    refresh_vulns_product_versions_task.apply_async(args=[], queue='default', retry=False)
    return JsonResponse("enqueued", safe=False)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def toggle_monitor_vuln(self, vuln_id):
    if set(['vuln_id', 'monitored', 'organization_id']).issubset(self.data.keys()) is False:
        return JsonResponse("error.", safe=False, status=500)

    vuln = get_object_or_404(Vuln, id=self.data['vuln_id'])
    if vuln is None or vuln_id != str(self.data['vuln_id']):
        return JsonResponse("error.", safe=False, status=500)
    else:
        organization_id = self.data['organization_id']
        org = organization.get_current_organization(user=self.user, org_id=organization_id)

        if self.data['monitored'] is True and vuln not in org.org_monitoring_list.vulns.all():
            org.org_monitoring_list.vulns.add(vuln)

        if self.data['monitored'] is False and vuln in org.org_monitoring_list.vulns.all():
            org.org_monitoring_list.vulns.remove(vuln)

            try:
                org_vuln_metadata = OrgVulnMetadata.objects.get(vuln=vuln_id, organization=org.id)
                org_vuln_metadata.status = 'undefined'
                org_vuln_metadata.save()
            except ObjectDoesNotExist:
                pass

    vuln.save()
    return JsonResponse("toggled.", safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vuln_stats(self):
    org_id = self.session.get('org_id', None)
    org = organization.get_current_organization(user=self.user, org_id=org_id)

    monitored_vendors = Vendor.objects.filter(id__in=org.org_monitoring_list.vendors.all())
    monitored_products = Product.objects.filter(id__in=org.org_monitoring_list.products.all())
    monitored_vulns = Vuln.objects.filter(id__in=org.org_monitoring_list.vulns.all())

    res = {
        'vulns': Vuln.objects.count(),
        'vulns_exploitable': Vuln.objects.filter(is_exploitable=True).count(),
        'exploits': ExploitMetadata.objects.count(),
        'threats': ThreatMetadata.objects.count(),
        'monitored': monitored_products.count() + monitored_vulns.count(),
        'monitored_vendors': monitored_vendors.count(),
        'monitored_products': monitored_products.count(),
        'monitored_vulns': monitored_vulns.count(),
    }
    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_monitored_vuln_stats(self):
    org_id = self.session.get('org_id', None)
    org = organization.get_current_organization(user=self.user, org_id=org_id)

    # monitored_vendors = Vendor.objects.filter(id__in=org.org_monitoring_list.vendors.all()).only('id')
    # monitored_products = Product.objects.filter(id__in=org.org_monitoring_list.products.all()).only('id')
    # monitored_packages = Package.objects.filter(id__in=org.org_monitoring_list.packages.all()).only('id')
    # monitored_vulns = Vuln.objects.filter(id__in=org.org_monitoring_list.vulns.all()).only('id')
    # monitored_exploits = ExploitMetadata.objects.filter(id__in=org.org_monitoring_list.vulns.all())
    # monitored_threats = ThreatMetadata.objects.filter(id__in=org.org_monitoring_list.vulns.all())

    # monitored_packages_vulns = Vuln.objects.prefetch_related('packages').filter(packages__in=monitored_packages).only('id')
    # monitored_products_vulns = Vuln.objects.prefetch_related('products').filter(products__in=monitored_products).only('id')
    # monitored_vendors_vulns = Vuln.objects.prefetch_related('products', 'products__vendor').filter(products__vendor__in=monitored_vendors).only('id')

    # all_monitored_vulns = (monitored_vulns | monitored_packages_vulns | monitored_products_vulns | monitored_vendors_vulns).distinct()

    monitored_vendors = Vendor.objects.filter(id__in=org.org_monitoring_list.vendors.all().only('id')).only('id')
    monitored_products = Product.objects.filter(id__in=org.org_monitoring_list.products.all().only('id')).only('id')
    monitored_packages = Package.objects.filter(id__in=org.org_monitoring_list.packages.all().only('id')).only('id')
    monitored_vulns = Vuln.objects.filter(id__in=org.org_monitoring_list.vulns.all().only('id')).only('id', 'is_exploitable')
    monitored_exploits = ExploitMetadata.objects.filter(id__in=org.org_monitoring_list.vulns.all().only('id')).only('id')
    monitored_threats = ThreatMetadata.objects.filter(id__in=org.org_monitoring_list.vulns.all().only('id')).only('id')

    all_monitored_vulns = Vuln.objects.prefetch_related('packages', 'products', 'products__vendor').filter(
        Q(id__in=org.org_monitoring_list.vulns.all().only('id')) |
        Q(packages__in=monitored_packages) |
        Q(products__in=monitored_products) |
        Q(products__vendor__in=monitored_vendors)
    ).only('id', 'is_exploitable', 'access').distinct()
    
    res = {
        'vulns':  {
            'count': all_monitored_vulns.count(),
            'exploitable': all_monitored_vulns.filter(is_exploitable=True).count(),
            'remote': all_monitored_vulns.filter(access__vector='NETWORK').count(),
        },
        'metadata': {
            'count': monitored_exploits.count() + monitored_threats.count(),
            'exploits': monitored_exploits.count(),
            'threats': monitored_threats.count(),
        },
        'monitored': {
            'count': monitored_products.count() + monitored_vulns.count(),
            'vendors': monitored_vendors.count(),
            'products': monitored_products.count(),
            'packages': monitored_packages.count(),
            'vulnerabilities': monitored_vulns.count(),
        },

    }
    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_vulns(self):
    MAX_VULNS = 20
    MAX_TIMEDELTA_DAYS = 30
    if self.GET.get('timedelta', None) and self.GET.get('timedelta').isnumeric():
        MAX_TIMEDELTA_DAYS = int(self.GET.get('timedelta'))+30

    vulns = list(Vuln.objects.all()
        .only('id', 'cveid', 'summary', 'score')
        .values('id', 'cveid', 'summary', 'score')
        .order_by('-updated_at').distinct()[:MAX_VULNS])

    exploits = []
    exploit_list = list(ExploitMetadata.objects.all().only('id', 'source', 'link', 'trust_level', 'availability', 'maturity').distinct('link', 'updated_at').order_by('-updated_at', 'link')[:MAX_VULNS])
    for exploit in exploit_list:
        exploits.append({
            'source': exploit.source,
            'link': exploit.link,
            'trust_level': exploit.trust_level,
            'scope': 'public',
            'relevancy_level': exploit.get_relevancy_level()
        })

    org_id = self.session.get('org_id', None)
    org = organization.get_current_organization(user=self.user, org_id=org_id)
    monitored_products = org.org_monitoring_list.products.all().prefetch_related('vendor')
    monitored_vulns = org.org_monitoring_list.vulns.all().prefetch_related(
        'exploitmetadata_set', 'orgexploitmetadata_set', 
        'orgexploitmetadata_set__organization', 
        'products', 'products__vendor', 'cwe'
    ).annotate(
        oem_count=Count('orgexploitmetadata')
    )
    
    monitored_vulns_list = list()
    for mv in monitored_vulns:
        mv_products = [{'id': p.id, 'name': p.name, 'vendor': p.vendor.name} for p in mv.products.all()]
        mv_exploitcount = mv.exploitmetadata_set.count()
        mv_orgexploitcount = mv.oem_count
        monitored_vulns_list.append({
            'id': mv.id,
            'cveid': mv.cveid,
            'summary': mv.summary,
            'access': mv.access,
            'impact': mv.impact,
            'score': mv.score,
            'cvss': mv.cvss,
            'cvss3': mv.cvss3,
            'products': mv_products,
            'updated_at': mv.updated_at,
            'is_confirmed': mv.is_confirmed,
            'exploit_count': mv_exploitcount+mv_orgexploitcount
        })

    monitored_vulns_list_ids = [o['id'] for o in monitored_vulns_list]
    monitored_vulns_list_update = datetime.now() - timedelta(days=MAX_TIMEDELTA_DAYS)
    latest_vulns = Vuln.objects.exclude(
        id__in=monitored_vulns_list_ids
    ).filter(
        modified__gte=monitored_vulns_list_update,
        vulnerable_products__isnull=False,
        products__in=monitored_products
    ).prefetch_related(
        'exploitmetadata_set', 
        'orgexploitmetadata_set', 'orgexploitmetadata_set__organization',
        'products', 'products__vendor'
    ).annotate(
        oem_count=Count('orgexploitmetadata')
    ).order_by('-updated_at').distinct()
    
    for lv in latest_vulns:
        # Check if vulnerable products are monitored
        lv_exploitcount = lv.exploitmetadata_set.count()
        lv_orgexploitcount = lv.oem_count
        monitored_vulns_list.append(dict({
            'id': lv.id,
            'cveid': lv.cveid,
            'summary': lv.summary,
            'access': lv.access,
            'impact': lv.impact,
            'score': lv.score,
            'cvss': lv.cvss,
            'cvss3': lv.cvss3,
            'products': [{'id': p.id, 'name': p.name, 'vendor': p.vendor.name} for p in lv.products.all()],
            'exploit_count': lv_exploitcount+lv_orgexploitcount,
            'is_confirmed': lv.is_confirmed,
            'updated_at': lv.updated_at
        }))

    res = {
        'vulns': vulns,
        'exploits': exploits,
        'monitored_vulns': monitored_vulns_list,
    }
    return JsonResponse(res, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def email_daily_report(self):
    email_daily_report_task.apply_async(args=[], queue='alerts', retry=False)
    return JsonResponse("enqueued", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def email_weekly_report(self):
    email_weekly_report_task.apply_async(args=[], queue='alerts', retry=False)
    return JsonResponse("enqueued", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def email_monthly_report(self):
    email_monthly_report_task.apply_async(args=[], queue='alerts', retry=False)
    return JsonResponse("enqueued", safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def slack_alert_vuln(self, vuln_id):
    slack_alert_vuln_task.apply_async(args=[vuln_id, "update"], queue='alerts', retry=False)
    return JsonResponse("enqueued", safe=False)
