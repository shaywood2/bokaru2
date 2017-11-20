import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import utc

from event.models import Event, Pick
from .forms import SearchForm

# Get an instance of a logger
logger = logging.getLogger(__name__)


def index(request):
    if request.user.is_authenticated():
        return render(request, 'web/index.html', {'user': request.user})
    else:
        return render(request, 'web/index_landing.html')


def search(request):
    search_result = []
    placeholder = "Dog Lovers"
    if request.method == 'POST':
        form = SearchForm(request.POST)
        # logger.error('This is an error 5: ' + form.errors.as_json())

        if form.is_valid():
            # Full text search
            search_result = Event.objects.search_text(form.cleaned_data['search_term'])
            # Filter out past events
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            search_result = search_result.filter(startDateTime__gte=now)
            placeholder = form.cleaned_data['search_term']
            # TODO: BASED ON USER'S PROFILE:
            # TODO: select 1 or 2 genders
            # TODO: select age range
            # TODO: filter out full events
            # TODO: search by event size
            # TODO: search by filled percentage

    else:
        form = SearchForm

    context = {
        'search_result': search_result,
        'form': form,
        'search_placeholder': placeholder,
    }

    return render(request, 'web/search.html', context)


@login_required
def matches(request):
    # Get all matches by user
    picks = Pick.objects.get_all_matches_by_user(request.user)
    # Sort picks by event date
    picks = sorted(picks.items(), key=lambda pick: pick[0].startDateTime)
    context = {'pick_map': picks}

    return render(request, 'web/matches.html', context)


@login_required
def my_events(request):
    events = Event.objects.get_all_by_user(request.user)
    context = {
        'events': events,
        'test': "My Events Page",
    }

    return render(request, 'web/my_events.html', context)


def terms_of_use(request):
    context = {
        'test': "Terms of Use Page",
    }

    return render(request, 'web/terms_of_use.html', context)


def how_it_works(request):
    context = {
        'test': "How It Works Page",
    }

    return render(request, 'web/how_it_works.html', context)


def privacy_policy(request):
    context = {
        'test': "Privacy Policy Page",
    }

    return render(request, 'web/privacypolicy.html', context)
