# from opentok import OpenTok, MediaModes, OutputModes

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from chat import utils
from web.models import Event, Pick

api_key = "45689752"
api_secret = "8b928a5fcc3d59f30bd1e8577171cef2676edecf"


# Initialize API
# opentok = OpenTok(api_key, api_secret)
# Create a shared session
# session = opentok.create_session(media_mode=MediaModes.routed)

@login_required
def live_event(request):
    # Get the current event
    event = Event.objects.get_current(request.user)

    if event is None:
        event = Event.objects.get_next(request.user)

        return render(request, 'chat/no_live.html', {'event': event})

    if event.is_in_progress():
        # Get current date
        date = utils.get_current_date(request.user.id, event.id)

        context = {
            'event': event,
            'date': date
        }

        if date is None:
            # No next date, the event should be over
            # TODO: get results
            context = {
                'event': event
            }
            return render(request, 'chat/post_live.html', context)

        if date['is_active']:
            return render(request, 'chat/live.html', context)
        else:
            return render(request, 'chat/live_break.html', context)

    if event.is_starting_soon():
        dates = utils.get_user_dates(request.user.id, event.id)
        date_list = []

        for k, v in dates.items():
            date_list.append(v)

        context = {
            'event': event,
            'dates': date_list
        }

        return render(request, 'chat/lobby.html', context)

    if event.is_ended_recently():
        # TODO: get results
        context = {
            'event': event
        }

        return render(request, 'chat/post_live.html', context)


@login_required
def session_create(request):
    data = {
        'apiKey': api_key,
        'sessionId': '123',  # session.session_id,
        'token': '456'  # opentok.generate_token(session.session_id)
    }
    return JsonResponse(data)


@login_required
def token_create(request, session_id):
    data = {
        'token': '456'  # opentok.generate_token(session_id)
    }
    return JsonResponse(data)


@login_required
def get_user_dates(request, event_id):
    result = utils.get_user_dates(request.user.id, event_id)
    if result is not None:
        return JsonResponse(result)
    else:
        return JsonResponse({})


@login_required
def get_upcoming_event(request):
    event = Event.objects.get_current(request.user.id)
    result = {}
    if event is not None:
        result = {'id': event.id, 'name': event.name, 'locationName': event.locationName,
                  'description': event.description, 'startDateTime': event.startDateTime,
                  'endDateTime': event.endDateTime, 'dateDuration': event.dateDuration,
                  'breakDuration': event.breakDuration}
    return JsonResponse(result)


@login_required
def get_current_date(request, event_id):
    result = utils.get_current_date(request.user.id, event_id)
    if result is not None:
        return JsonResponse(result)
    else:
        return JsonResponse({})


@login_required
def create_pick(request, target_user_id, event_id, response):

    pick = Pick.objects.pick_by_id(request.user, target_user_id, event_id, response)

    return JsonResponse({'picker': str(pick.picker), 'picked': str(pick.picked), 'event': str(pick.event),
                         'response': pick.response})
