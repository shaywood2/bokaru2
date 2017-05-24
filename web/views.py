from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.contrib import messages

from .forms import EventForm, EventGroupForm
from .models import Event, EventGroup
from account.models import Account


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
    group1_participants = Account.objects.filter(user__in=event_groups[0].participants.all())
    group2_participants = {}
    group2_filled_percentage = 0
    group2_spots_left = 0
    if num_groups > 1:
        group2_filled_percentage = float(event_groups[1].participants.count()) \
                                   / event_groups[1].participantsMaxNumber * 100
        group2_spots_left = event_groups[1].participantsMaxNumber - event_groups[1].participants.count()
        group2_participants = Account.objects.filter(user__in=event_groups[1].participants.all())

    context = {
        'event': selected_event,
        'num_groups': num_groups,
        'groups': event_groups,
        'group1_filled_percentage': group1_filled_percentage,
        'group2_filled_percentage': group2_filled_percentage,
        'group1_spots_left': group1_spots_left,
        'group2_spots_left': group2_spots_left,
        'group1_participants': group1_participants,
        'group2_participants': group2_participants,
    }
    return render(request, 'web/event.html', context)


def event_create(request):
    current_user = request.user

    GroupFormSet = formset_factory(EventGroupForm, extra=1, min_num=1, validate_min=True)

    if request.method == 'POST':
        event_form = EventForm(request.POST)
        group_formset = GroupFormSet(request.POST)
        if all([event_form.is_valid(), group_formset.is_valid()]):
            new_event = event_form.save(commit=False)
            new_event.creator = current_user
            new_event.save()
            for inline_form in group_formset:
                if inline_form.cleaned_data:
                    group = inline_form.save(commit=False)
                    group.event = new_event
                    group.save()

            return HttpResponseRedirect(reverse('web:event_view', kwargs={'event_id': new_event.id}))
    else:
        event_form = EventForm()
        group_formset = GroupFormSet()

    context = {
        'event_form': event_form,
        'group_formset': group_formset,
    }

    return render(request, 'web/eventcreate.html', context)


def eventedit(request):
    context = {
        'test': "Event Edit Page",
    }

    return render(request, 'web/eventedit.html', context)


def event_join(request, group_id):
    current_user = request.user
    selected_group = get_object_or_404(EventGroup, pk=group_id)
    selected_event = selected_group.event

    # Attempt to add user to the group
    try:
        selected_group.add_participant(current_user)
        return HttpResponseRedirect(reverse('web:event_joined'))
    except Exception as e:
        messages.add_message(request, messages.ERROR, str(e))

    return HttpResponseRedirect(reverse('web:event_view', kwargs={'event_id': selected_event.id}))


def participants(request):
    context = {
        'test': "Event Participants Page",
    }

    return render(request, 'web/participants.html', context)


def event_joined(request):
    context = {
        'test': "Event Joined Page",
    }

    return render(request, 'web/eventjoined.html', context)


def payment(request):
    context = {
        'test': "Event Pay Page",
    }

    return render(request, 'web/payment.html', context)


def matches(request):
    context = {}

    return render(request, 'web/matches.html', context)


def lobby(request):
    context = {}

    return render(request, 'web/lobby.html', context)


def match(request):
    context = {}

    return render(request, 'web/match.html', context)


def live(request):
    context = {}

    return render(request, 'web/live.html', context)


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
