from django.conf import settings
from rest_framework import authentication


class CustomTokenAuthentication(authentication.TokenAuthentication):
    def __init__(self):
        super().__init__()

    def authenticate(self, request):
        return self.authenticate(request)
