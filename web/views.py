import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.shortcuts import render

from account.models import Account, UserPreference
from event.models import Event, Pick
from .forms import SearchForm

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

    context = {
        'future_events': future_events,
        'past_events': past_events
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
    if request.user.is_authenticated:
        # Get user's preferences
        preferences = UserPreference.objects.get(user=request.user)
    else:
        # Create default preferences
        preferences = UserPreference()

    # Get default search parameters
    search_params = model_to_dict(preferences)

    # Get from from request
    if request.GET.get('cityName'):
        form = SearchForm(request.GET, instance=preferences)
        if form.is_valid():
            # Save updated search parameters
            form.save()
            # Update search parameters from the form
            search_params = form.cleaned_data
    else:
        form = SearchForm(instance=preferences)

    if request.user.is_authenticated:
        # Get user's account
        account = Account.objects.get(user=request.user)
        search_params['sexual_identity'] = account.sexualIdentity
        search_params['age'] = account.age

    # logger.info('Search for: ' + str(search_params))

    # Perform search
    search_result = Event.objects.search(**search_params)
    num_results = len(search_result)

    # Figure out view type
    view_type = request.GET.get('view_type')
    page_size = 5
    if not view_type:
        view_type = 'list'
    if view_type == 'grid':
        page_size = 12

    # Apply pagination
    paginator = Paginator(search_result, page_size)
    page = request.GET.get('page')
    search_result = paginator.get_page(page)

    context = {
        'view_type': view_type,
        'search_result': search_result,
        'num_results': num_results,
        'page_range': range(1, paginator.num_pages + 1),
        'form': form
    }

    return render(request, 'web/search.html', context)


def search_results(request):
    search_result = []
    num_results = 0
    page_size = 5

    if request.user.is_authenticated:
        # Get user's preferences
        preferences = UserPreference.objects.get(user=request.user)
        form = SearchForm(request.GET, instance=preferences)
    else:
        form = SearchForm(request.GET)

    if form.is_valid():
        # Save updated preferences
        if request.user.is_authenticated:
            form.save()
            logger.info('prefs saved')

        if form.cleaned_data.get('view_type') == 'grid':
            page_size = 12

        # Perform search
        search_result = Event.objects.search(**form.cleaned_data)
        num_results = len(search_result)
    else:
        logger.error(form.errors)

    # Apply pagination
    paginator = Paginator(search_result, page_size)
    page = request.GET.get('page')
    search_result = paginator.get_page(page)

    context = {
        'search_result': search_result,
        'num_results': num_results,
        'page_range': range(1, paginator.num_pages + 1),
        'form': form
    }

    return render(request, 'web/search.html', context)


def terms_of_use(request):
    return render(request, 'web/terms_of_use.html')


def how_it_works(request):
    return render(request, 'web/how_it_works.html')


def privacy_policy(request):
    return render(request, 'web/privacypolicy.html')
