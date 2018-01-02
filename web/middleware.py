from event.models import Event


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
