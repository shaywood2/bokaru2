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
        return '<div id="event_alert" style="width: 100%;height: 55px;' \
               'background-color: #e74c3c;text-align: center;background: #e74c3c;font-size: 16pt;' \
               'line-height: 55px;font-family: &quot;Open Sans&quot;, Arial, sans-serif;color: white;" >' \
               '<div onclick="document.getElementById(&quot;event_alert&quot;).style.display = &quot;none&quot;" ' \
               'style="float: right; cursor: pointer; width: 30px; height: 30px; background-color: white; ' \
               'margin-top: 12px; margin-right: 10px;"><div style="margin-top: -13px;"><i class="fa fa-times" ' \
               'style="color: #e74c3c" aria-hidden="true"></i></div>' \
               '</div><div onclick="document.location.href=&quot;google.ca&quot;">' \
               'Event Starting Soon.</div></div>'

    # TODO: include redirect javascript
    if event.is_in_progress():

        return '<div id="event_alert" style="width: 100%;height: 55px;' \
               'background-color: #e74c3c;text-align: center;background: #e74c3c;font-size: 16pt;' \
               'line-height: 55px;font-family: &quot;Open Sans&quot;, Arial, sans-serif;color: white;" >' \
               '<div onclick="document.getElementById(&quot;event_alert&quot;).style.display = &quot;none&quot;" ' \
               'style="float: right; cursor: pointer; width: 30px; height: 30px; background-color: white; ' \
               'margin-top: 12px; margin-right: 10px;"><div style="margin-top: -13px;"><i class="fa fa-times" ' \
               'style="color: #e74c3c" aria-hidden="true"></i></div>' \
               '</div><div>' \
               '<a style="color: white" href=&quot;test.com&quot;>Event In Progress. Click to join.</a></div></div>'


