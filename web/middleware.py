import logging

import pytz
from django.utils import timezone

from account.models import UserPreference
from event.models import Event

LOGGER = logging.getLogger(__name__)


# Middleware to look up an upcoming event for a logged in user
class UpcomingEventMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            current_event = Event.objects.get_current(user)
            request.current_event = current_event

        response = self.get_response(request)

        return response


# Middleware to look up and activate user's timezone
class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            tz_name = UserPreference.objects.get_timezone_name(user)
            timezone.activate(pytz.timezone(tz_name))
        else:
            timezone.deactivate()

        response = self.get_response(request)

        return response
