import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from opentok import OpenTok

from event.models import Event, Pick
from .models import Conversation
from .utils import get_current_date, get_user_dates

api_key = settings.TOKBOX_KEY
api_secret = settings.TOKBOX_SECRET

# Get an instance of a logger
LOGGER = logging.getLogger(__name__)


@login_required
def live_event(request):
    # Get the current event
    event = Event.objects.get_current(request.user)

    if event is None:
        next_event = Event.objects.get_next(request.user)

        return render(request, 'chat/no_live.html', {'next_event': next_event})

    if event.is_in_progress():
        # Get current date
        date = get_current_date(request.user, event)

        if date is None:
            # No next date, the event should be over
            matches = Pick.objects.get_all_matches_by_user_and_event(request.user, event)

            context = {
                'event': event,
                'matches': matches
            }
            return render(request, 'chat/post_live.html', context)

        if date.is_break:
            context = {
                'event': event,
                'is_break': True,
                'time_passed': date.time_passed,
                'time_until_reload': date.time_until_reload
            }

            return render(request, 'chat/live_break.html', context)

        if date.is_active:
            # Chat is in progress
            # Create a token
            opentok = OpenTok(api_key, api_secret)
            connection_metadata = 'username=' + request.user.username + ',eventId=' + str(event.id)
            token = opentok.generate_token(date.session_id, data=connection_metadata)

            # Mark conversation as token requested
            Conversation.objects.mark_token_requested(date.conversation_id)

            context = {
                'event': event,
                'is_break': False,
                'is_active': True,
                'user': date.user,
                'account': date.account,
                'memo': date.memo,
                'sessionID': date.session_id,
                'token': token,
                'tokbox_api_key': api_key,
                'time_passed': date.time_passed,
                'time_until_reload': date.time_until_reload
            }

            return render(request, 'chat/live.html', context)
        else:
            # Making a pick
            # Look up the previous pick result for the same pair and event
            pick_response = Pick.objects.get_response(request.user, date.user, event)

            context = {
                'event': event,
                'is_break': False,
                'is_active': False,
                'user': date.user,
                'account': date.account,
                'memo': date.memo,
                'time_passed': date.time_passed,
                'time_until_reload': date.time_until_reload,
                'pick_response': pick_response
            }

            return render(request, 'chat/live_pick.html', context)

    if event.is_starting_soon():
        dates = get_user_dates(request.user, event)

        context = {
            'event': event,
            'dates': dates,
            'time_until_reload': event.get_seconds_until_start()
        }

        return render(request, 'chat/lobby.html', context)

    if event.is_ended_recently():
        matches = Pick.objects.get_all_matches_by_user_and_event(request.user, event)

        context = {
            'user': request.user,
            'event': event,
            'matches': matches,
        }

        return render(request, 'chat/post_live.html', context)


# # TODO: Temp method, delete later
# def live_event_test(request, user1, user2):
#     LOGGER.info('user ' + user1 + ' calls user ' + user2)
#     opentok = OpenTok(api_key, api_secret)
#
#     # Look up the session ID
#     key = '1' + '|' + str(user1) + '|' + str(user2)
#     session_id = cache.get(key)
#     if session_id is None:
#         key = '1' + '|' + str(user2) + '|' + str(user1)
#         session_id = cache.get(key)
#
#     # Create a session if it is missing
#     if session_id is None:
#         # Create a session that attempts to send streams directly between clients (falling back
#         # to use the OpenTok TURN server to relay streams if the clients cannot connect):
#         session = opentok.create_session()
#         # A session that uses the OpenTok Media Router, which is required for archiving
#         # session = opentok.create_session(media_mode=MediaModes.routed, archive_mode=ArchiveModes.always)
#         session_id = session.session_id
#         key = '1' + '|' + str(user1) + '|' + str(user2)
#         cache.set(key, session_id, 60 * 60 * 5)
#
#     # Create a token
#     connection_metadata = 'username=' + user1 + ',eventId=4'
#     token = opentok.generate_token(session_id, data=connection_metadata)
#     LOGGER.info('created token: ' + str(token))
#
#     context = {
#         'tokbox_api_key': api_key,
#         'sessionID': session_id or 'wait',
#         'token': token
#     }
#
#     return render(request, 'chat/test.html', context)


@login_required
def create_pick(request, target_user_id, event_id, response):
    pick = Pick.objects.pick_by_id(request.user, target_user_id, event_id, response)

    return JsonResponse({'picker': str(pick.picker), 'picked': str(pick.picked), 'event': str(pick.event),
                         'response': pick.response})
