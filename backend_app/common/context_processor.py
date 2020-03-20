from django.conf import settings


def site(request):
    return {'BASE_URL': settings.BASE_URL}
