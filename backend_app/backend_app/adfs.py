from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([AllowAny])
def custom_adfs_connection(request):
    """
    Return JWT that was fetched from either an ADFS server or 
    this django app itself
    """

    username = request.data["username"]
    password = request.data["password"]

    # payload for adfs
    payload = {
            "grant_type": "password",
            "resource": settings.AUTH_ADFS["RELYING_PARTY_ID"],
            "client_id": settings.AUTH_ADFS["CLIENT_ID"],
            "username":username,
            "password":password,
            }
    adfs_res = requests.post("https://"+settings.AUTH_ADFS["SERVER"]+"/adfs/oauth2/token",
            data=payload,
            verify=False
            )

    if adfs_res.status_code==200:
        adfs_res = adfs_res.json()
        jwt_from_adfs = {
                "access":adfs_res["access_token"],
                "refresh":adfs_res["refresh_token"]
        }
        return JsonResponse(jwt_from_adfs,status=200)

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
