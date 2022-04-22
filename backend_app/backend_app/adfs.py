from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse, HttpResponseRedirect

# from django.shortcuts import redirect
# from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from organizations.models import Organization, OrganizationUser, OrganizationOwner
import requests
# import base64

if hasattr(settings, 'AUTH_ADFS'):
    from django_auth_adfs.config import provider_config


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_sso_connection(request):
    """Check authentication either from an ADFS server or app itself."""
    username = request.data["username"]
    password = request.data["password"]

    # payload for adfs
    payload = {
        "grant_type": "password",
        "resource": settings.AUTH_ADFS["RELYING_PARTY_ID"],
        "client_id": settings.AUTH_ADFS["CLIENT_ID"],
        "username": username,
        "password": password,
    }

    adfs_res = requests.post(
        "https://" + settings.AUTH_ADFS["SERVER"] + "/adfs/oauth2/token",
        data=payload,
        verify=False
    )

    if adfs_res.status_code == 200:
        # Create utser if not exists
        user = get_user_model().objects.filter(username=username, is_active=True).first()
        if user is None:
            user = get_user_model().objects.create(username=username, email=username)

        # Create a personal organization, organization user & owner if not exists
        if user.organizations_organization.count() == 0:
            personal_org = Organization.objects.create(
                is_active=True,
                name="Private"
            )
            personal_org.save()
            personal_org.slug = "{}-{}".format(personal_org.slug, user.email)
            personal_org.save()

            personal_org_user = OrganizationUser.objects.create(
                user=user,
                organization=personal_org,
                is_admin=True)
            personal_org_user.save()

            personal_org_owner = OrganizationOwner.objects.create(
                organization=personal_org,
                organization_user=personal_org_user
            )
            personal_org_owner.save()

        refresh = RefreshToken.for_user(user)
        token_pair = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return JsonResponse(token_pair, status=200)

    # testing with django's users
    user = authenticate(username=username, password=password)

    if user is None:
        return Response("Invalid credentials", status=401)

    else:
        refresh = RefreshToken.for_user(user)
        token_pair = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return JsonResponse(token_pair, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def custom_sso_callback(request):
    code = request.GET.get("code", None)
    if code is None:
        # Return an error message
        return JsonResponse({"status": "error", "message": "No authorization code was provided."}, status=400)

    try:
        user = authenticate(request=request, authorization_code=code)
    except Exception:
        return JsonResponse({"status": "error", "message": "Authentication failed."}, status=500)
    # except MFARequired:
    #     return redirect(provider_config.build_authorization_endpoint(request, force_mfa=True))
    # print(user)

    if user:
        if user.is_active:
            refresh = RefreshToken.for_user(user)
            token_pair = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            # return JsonResponse(token_pair, status=200)
            return HttpResponseRedirect(f"/#/auth-sso?code=1&access={token_pair['access']}&refresh={token_pair['refresh']}", token_pair)
        else:
            return JsonResponse({"status": "error", "message": "Your account is disabled."}, status=403)
    else:
        return JsonResponse({"status": "error", "message": "Login failed."}, status=401)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sso_login_page(request):
    url = provider_config.build_authorization_endpoint(request)
    # url = url.replace("oauth2%2Fcallback", "%23%2Fauth-sso")
    # url = url.replace("oauth2%2Fcallback", "auth-sso")
    return JsonResponse({"url": url})
