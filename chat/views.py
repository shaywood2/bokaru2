from django.http import JsonResponse
from opentok import OpenTok, MediaModes, OutputModes

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

