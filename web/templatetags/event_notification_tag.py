from django.template import Library
from web.models import Event

register = Library()


@register.simple_tag
def event_notification(request):
    if not request.user.is_authenticated():
        return '<strong>LOL</strong>'

    # Get the current event
    event = Event.objects.get_current(request.user)

    if event is None:
        return '<strong>none</strong>'

    if event.is_starting_soon():
        return '<strong>event starting soon</strong>'

    if event.is_in_progress():
        return '<strong>event in progress, get going</strong>'
