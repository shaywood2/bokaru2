from django.template import Library
from web.models import Event
from chat import urls

register = Library()


@register.simple_tag
def event_notification(request):
    # Don't show anything on live event page
    if request.path.startswith('/' + urls.app_name):
        return ''

    # Don't show anything if user is not logged in
    if not request.user.is_authenticated():
        return ''

    # Get the current event
    event = Event.objects.get_current(request.user)

    # Don't show anything if no event is coming up in 1 hour
    if event is None:
        return ''

    if event.is_starting_soon():
        return '<strong>event starting soon</strong>'

    # TODO: include redirect javascript
    if event.is_in_progress():
        return '<strong>event starting soon</strong>'