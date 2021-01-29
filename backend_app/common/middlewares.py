from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

import json


class NonHtmlDebugToolbarMiddleware(MiddlewareMixin):
    """
    The Django Debug Toolbar usually only works for views that return HTML.
    This middleware wraps any JSON response in HTML if the request
    has a 'debug' query parameter (e.g. http://localhost/foo?debug)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        if request.GET.get('debug_me_please') and response.status_code == 200:
            # if response['Content-Type'] == 'application/json':
            content = json.dumps(json.loads(response.content), sort_keys=True, indent=2)
            response = HttpResponse(u'<html><body><pre>{}</pre></body></html>'.format(content))

        # Code to be executed for each request/response after
        # the view is called.

        return response
