import base64
import logging

from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse

from . import hourly_scripts

logger = logging.getLogger(__name__)


def activate_events(request):
    # Check login credentials
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == 'basic':
                decoded_bytes = base64.b64decode(auth[1])
                decoded_string = decoded_bytes.decode('latin-1')
                username, password = decoded_string.split(':')
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        request.user = user

                        # Call activation script
                        result = hourly_scripts.activate_events()
                        response = JsonResponse(result, safe=False)
                        return response

    response = HttpResponse()
    response.status_code = 401
    return response
