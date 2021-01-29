from django.conf import settings
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication


class CustomUserRateThrottle(UserRateThrottle):
    scope = "custom"

    def __init__(self):
        super().__init__()

    def allow_request(self, request, view):
        """
        Override rest_framework.throttling.SimpleRateThrottle.allow_request

        Check to see if the request should be throttled.

        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """

        # No throttling check for admins
        if settings.RESTRICTED_MODE is False or request.user.is_superuser or request.user.is_staff:
            return True

        check_api_ratio = False
        if isinstance(request._authenticator, TokenAuthentication):
            check_api_ratio = True
        elif isinstance(request._authenticator, JWTAuthentication) or isinstance(request._authenticator, SessionAuthentication):
            if request.META.get('CSRF_COOKIE') in [None, '']:
                check_api_ratio = True

        if check_api_ratio is False:
            return True

        if request.user.is_authenticated:
            if 'api_throttle_rate' in request.user.profile.keys() and request.user.profile['api_throttle_rate'] not in [-1, 'unlimited']:
                user_daily_limit = int(request.user.profile['api_throttle_rate'].split('/')[0])
                # Override the default from settings.py
                self.duration = 86400
                self.num_requests = user_daily_limit
            else:
                # No limit == unlimited plan
                return True

        # Original logic from the parent method...

        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()

        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()


# https://stackoverflow.com/questions/34538695/django-rest-framework-per-user-throttles
