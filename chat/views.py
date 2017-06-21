from django.http import JsonResponse
from opentok import OpenTok, MediaModes, OutputModes
from django.contrib.auth.models import User

from chat import utils

api_key = "45689752"
api_secret = "8b928a5fcc3d59f30bd1e8577171cef2676edecf"


# Initialize API
# opentok = OpenTok(api_key, api_secret)
# Create a shared session
# session = opentok.create_session(media_mode=MediaModes.routed)


def session_create(request):
    data = {
        'apiKey': api_key,
        'sessionId': '123',  # session.session_id,
        'token': '456'  # opentok.generate_token(session.session_id)
    }
    return JsonResponse(data)


def token_create(request, session_id):
    data = {
        'token': '456'  # opentok.generate_token(session_id)
    }
    return JsonResponse(data)


def get_user_dates(request, event_id, user_id):
    date_matrix = utils.get_date_matrix(event_id)
    user_id_int = int(user_id)
    if user_id_int in date_matrix:
        result = {}
        for date_num in date_matrix[user_id_int]:
            # Get user
            # TODO: get account instead of user model
            user = User.objects.get(pk=int(date_matrix[user_id_int][date_num]))
            result[date_num] = {'username': user.username, 'id': user.id}

        return JsonResponse(result)
    else:
        return JsonResponse({})
