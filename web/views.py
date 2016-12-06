from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect

from .forms import EventForm, EventGroupForm
from .models import Event, EventGroup

def index(request):
    context = {
        'user': request.user,
    }
    return render(request, 'web/index.html', context)


def test(request):
    context = {
        'test': "Test Page",
    }

    return render(request, 'web/test.html', context)


def search(request):
    context = {
        'test': "Search Page",
    }

    return render(request, 'web/search.html', context)


def results(request):
    context = {
        'test': "Search Results Page",
    }

    return render(request, 'web/results.html', context)


def event(request):
    context = {
        'test': "Event Detail Page",
    }

    return render(request, 'web/event.html', context)


def event_view(request, event_id):
    selected_event = get_object_or_404(Event, pk=event_id)
    event_groups = list(selected_event.eventgroup_set.all())
    num_groups = len(event_groups)

    group1_filled_percentage = float(event_groups[0].participants.count()) / event_groups[0].participantsMaxNumber * 100
    group1_spots_left = event_groups[0].participantsMaxNumber - event_groups[0].participants.count()

    if num_groups > 1:
        group2_filled_percentage = float(event_groups[1].participants.count())\
                                   / event_groups[1].participantsMaxNumber * 100
        group2_spots_left = event_groups[1].participantsMaxNumber - event_groups[1].participants.count()

    context = {
        'event': selected_event,
        'num_groups': num_groups,
        'groups': event_groups,
        'group1_filled_percentage': group1_filled_percentage,
        'group2_filled_percentage': group2_filled_percentage,
        'group1_spots_left': group1_spots_left,
        'group2_spots_left': group2_spots_left
    }
    return render(request, 'web/event.html', context)


def event_create(request):
    current_user = request.user

    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, user=current_user)
        event_group1_form = EventGroupForm(request.POST, request.FILES, user=current_user)
        if event_form.is_valid():
            event = event_form.save()
            return HttpResponseRedirect(reverse('web:event_view', kwargs={'event_id': event.id}))
    else:
        event_form = EventForm(user=current_user)

    context = {
        'event_form': event_form,
    }

    return render(request, 'web/eventcreate.html', context)


def eventedit(request):
    context = {
        'test': "Event Edit Page",
    }

    return render(request, 'web/eventedit.html', context)


def participants(request):
    context = {
        'test': "Event Participants Page",
    }

    return render(request, 'web/participants.html', context)


def eventjoined(request):
    context = {
        'test': "Event Joined Page",
    }

    return render(request, 'web/eventjoined.html', context)


def matches(request):
    context = {
        'test': "My Matches Page",
    }

    return render(request, 'web/matches.html', context)


def myevents(request):
    context = {
        'test': "My Events Page",
    }

    return render(request, 'web/myevents.html', context)


def termsofuse(request):
    context = {
        'test': "Terms of Use Page",
    }

    return render(request, 'web/termsofuse.html', context)


def howitworks(request):
    context = {
        'test': "How It Works Page",
    }

    return render(request, 'web/howitworks.html', context)


def privacypolicy(request):
    context = {
        'test': "Privacy Policy Page",
    }

    return render(request, 'web/privacypolicy.html', context)
