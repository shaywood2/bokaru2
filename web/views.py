import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect

from account.models import Account, UserPreference
from event.models import Event, Pick
from .forms import SearchForm
from .models import Place

# Get an instance of a logger
logger = logging.getLogger(__name__)


def index(request):
    if request.user.is_authenticated:
        return render(request, 'web/index.html', {'user': request.user})
    else:
        return render(request, 'web/index_landing.html')


@login_required
def my_events(request):
    future_events = Event.objects.get_all_future_by_user(request.user)
    past_events = Event.objects.get_all_past_by_user(request.user)
    created_events = Event.objects.get_all_created_by_user(request.user)

    context = {
        'future_events': future_events,
        'past_events': past_events,
        'created_events': created_events
    }

    return render(request, 'web/my_events.html', context)


@login_required
def my_matches(request):
    # Get all matches by user
    matches = Pick.objects.get_all_matches_by_user(request.user)

    context = {
        'match_map': matches.items()
    }

    return render(request, 'web/my_matches.html', context)


def search(request):
    sexual_identity_display = ''
    if request.user.is_authenticated:
        # Get user's preferences
        preferences = UserPreference.objects.get(user=request.user)
        search_params = model_to_dict(preferences)
        # Get user's account
        account = Account.objects.get(user=request.user)
        search_params['sexual_identity'] = account.sexualIdentity
        search_params['age'] = account.age
        sexual_identity_display = account.sexualIdentityDisplay
    else:
        preferences = UserPreference()
        # Create default search parameters
        search_params = {
            'sexual_identity': 'female',
            'age': 25,
            'cityName': 'Toronto, ON, Canada',
            'cityNameShort': 'Toronto',
            'cityLat': 43.653226,
            'cityLng': -79.3831843,
            'distance': 50,
            'distanceUnits': 'km',
            'lookingForGenderList': '',
            'lookingForAgeMin': 18,
            'lookingForAgeMax': 120
        }

    # Set search location from place
    if 'place' in request.session:
        place = request.session.pop('place')
        search_params['cityName'] = place['name']
        search_params['cityNameShort'] = place['shortName']
        search_params['cityLat'] = place['lat']
        search_params['cityLng'] = place['lng']

    # Figure out view type
    view_type = request.GET.get('view_type') or 'list'
    page_size = 5
    if view_type == 'grid':
        page_size = 12

    # Get from from request
    if request.GET.get('cityName'):
        form = SearchForm(request.GET, instance=preferences)
        if form.is_valid():
            # Save updated search parameters
            form.save()
            # Update search parameters from the form
            search_params = form.cleaned_data
    else:
        form_defaults = {
            'view_type': view_type,
            'sexual_identity': search_params['sexual_identity'],
            'age': search_params.get('age'),
            'cityName': search_params.get('cityName'),
            'cityNameShort': search_params.get('cityNameShort'),
            'cityLat': search_params.get('cityLat'),
            'cityLng': search_params.get('cityLng')
        }
        form = SearchForm(initial=form_defaults, instance=preferences)

    # Perform search
    # logger.info('search: ' + str(search_params))
    search_result = Event.objects.search(**search_params)
    num_results = len(search_result)

    # Apply pagination
    paginator = Paginator(search_result, page_size)
    page = request.GET.get('page')
    search_result = paginator.get_page(page)

    context = {
        'view_type': view_type,
        'search_result': search_result,
        'num_results': num_results,
        'page_range': range(1, paginator.num_pages + 1),
        'sexual_identity_display': sexual_identity_display,
        'form': form
    }

    return render(request, 'web/search.html', context)


def search_by_place(request, place_name):
    # Look up the place by name
    try:
        place = Place.objects.get(slug__iexact=place_name)
        request.session['place'] = model_to_dict(place)
    except Place.DoesNotExist:
        pass

    return redirect('web:search')


def privacy_statement(request):
    return render(request, 'web/privacy_statement.html')


def terms_of_service(request):
    return render(request, 'web/terms_of_service.html')


def refund_policy(request):
    return render(request, 'web/refund_policy.html')


def how_it_works(request):
    return render(request, 'web/how_it_works.html')


def about_us(request):
    return render(request, 'web/about_us.html')
