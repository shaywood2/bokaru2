import datetime
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, reverse, get_object_or_404
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt

from account.models import Account
from money.billing_logic import get_product_by_participant_number
from .forms import EventForm, EventGroupForm, SearchForm
from .models import Event, EventParticipant, EventGroup, Pick, Memo

# Get an instance of a logger
logger = logging.getLogger(__name__)


def index(request):
    context = {
        'user': request.user,
    }

    if request.user.is_authenticated():
        return render(request, 'web/index.html', context)
    else:
        # messages.success(request, 'Profile details updated.')
        return render(request, 'web/index_landing.html', context)


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


def results(request):
    context = {
        'test': "Search Results Page",
    }

    return render(request, 'web/results.html', context)


def event(request):

    groupparticipants = EventParticipant.objects.filter(user=request.user)
    eventgroups = EventGroup.objects.filter(eventparticipant__in=groupparticipants)
    events = Event.objects.filter(eventgroup__in=eventgroups)

    context = {
        'test2': [1, 2],
        'events': events,
        'test': "Event Detail Page",
    }

    return render(request, 'web/event.html', context)


def event_view(request, event_id):
    selected_event = get_object_or_404(Event, pk=event_id)
    event_groups = list(selected_event.eventgroup_set.all())

    # First group info
    group1_filled_percentage = float(event_groups[0].count_registered_participants()) \
                               / selected_event.maxParticipantsInGroup * 100
    group1_spots_left = selected_event.maxParticipantsInGroup - event_groups[0].count_registered_participants()
    group1_users = []
    for participant in event_groups[0].get_registered_participants():
        group1_users.append(participant.user)
    group1_participants = Account.objects.filter(user__in=group1_users)

    # Second group info
    group2_participants = {}
    group2_filled_percentage = 0
    group2_spots_left = 0
    if selected_event.numGroups > 1:
        group2_filled_percentage = float(event_groups[1].count_registered_participants()) \
                                   / selected_event.maxParticipantsInGroup * 100
        group2_spots_left = selected_event.maxParticipantsInGroup - event_groups[1].count_registered_participants()
        group2_users = []
        for participant in event_groups[1].get_registered_participants():
            group2_users.append(participant.user)
        group2_participants = Account.objects.filter(user__in=group2_users)

    # Check if user is registered
    is_registered = False
    if request.user.is_authenticated() and request.user is not None:
        is_registered = selected_event.is_registered(request.user)

    context = {
        'event': selected_event,
        'groups': event_groups,
        'num_groups': selected_event.numGroups,
        'group1_filled_percentage': group1_filled_percentage,
        'group2_filled_percentage': group2_filled_percentage,
        'group1_spots_left': group1_spots_left,
        'group2_spots_left': group2_spots_left,
        'group1_participants': group1_participants,
        'group2_participants': group2_participants,
        'is_registered': is_registered
    }
    return render(request, 'web/event.html', context)


@login_required
def event_create(request):
    current_user = request.user

    group_formset = formset_factory(EventGroupForm, extra=1, min_num=1, validate_min=True)

    if request.method == 'POST':
        event_form = EventForm(request.POST)
        group_formset = group_formset(request.POST)
        if all([event_form.is_valid(), group_formset.is_valid()]):
            new_event = event_form.save(commit=False)
            new_event.creator = current_user
            new_event.product = get_product_by_participant_number(
                new_event.maxParticipantsInGroup * new_event.numGroups)
            new_event.save()

            for inline_form in group_formset:
                if inline_form.cleaned_data:
                    group = inline_form.save(commit=False)
                    group.event = new_event
                    group.save()

            if 'upload_image' in request.FILES:
                image_file = request.FILES['upload_image'].read()

                # Get cropping parameters
                x = event_form.cleaned_data.get('crop_x')
                y = event_form.cleaned_data.get('crop_y')
                w = event_form.cleaned_data.get('crop_w')
                h = event_form.cleaned_data.get('crop_h')

                new_event.add_photo(image_file, x, y, w, h, 400)

            return HttpResponseRedirect(reverse('web:event_view', kwargs={'event_id': new_event.id}))
    else:
        event_form = EventForm()
        group_formset = group_formset()

    context = {
        'event_form': event_form,
        'group_formset': group_formset,
    }

    return render(request, 'web/eventcreate.html', context)


def event_edit(request):
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
        return HttpResponseRedirect(reverse('web:event_joined', kwargs={'event_id': selected_event.id}))
    except Exception as e:
        messages.add_message(request, messages.ERROR, str(e))

    return HttpResponseRedirect(reverse('web:event_view', kwargs={'event_id': selected_event.id}))


def participants(request):
    context = {
        'test': "Event Participants Page",
    }

    return render(request, 'web/participants.html', context)


def event_joined(request, event_id):
    selected_event = get_object_or_404(Event, pk=event_id)
    event_groups = list(selected_event.eventgroup_set.all())
    num_groups = len(event_groups)
    group1_spots_left = selected_event.maxParticipantsInGroup - event_groups[0].count_registered_participants()

    # group1_participants = Account.objects.filter(user__in=event_groups[0].participants.all())
    group1_participants = Account.objects.filter(
        user__in=event_groups[0].get_registered_participants().values_list('user'))
    group2_participants = {}
    group1_filled_percentage = float(event_groups[0].get_registered_participants().values_list(
        'user').count()) / selected_event.maxParticipantsInGroup * 100
    group2_spots_left = 0
    if num_groups > 1:
        group2_participants = Account.objects.filter(
            user__in=event_groups[1].get_registered_participants().values_list('user'))
        group2_spots_left = selected_event.maxParticipantsInGroup - event_groups[1].count_registered_participants()
        group2_filled_percentage = float(event_groups[1].get_registered_participants().values_list(
            'user').count()) / selected_event.maxParticipantsInGroup * 100

    context = {
        'test': "Event Joined Page",
        'num_groups': num_groups,
        'groups': event_groups,
        'event': selected_event,
        'group1_participants': group1_participants,
        'group2_participants': group2_participants,
        'group1_spots_left': group1_spots_left,
        'group2_spots_left': group2_spots_left,
        'group1_filled_percentage': group1_filled_percentage,
        'group2_filled_percentage': group2_filled_percentage,
    }

    return render(request, 'web/eventjoined.html', context)


def payment(request):
    context = {
        'test': "Event Pay Page",
    }

    return render(request, 'web/payment.html', context)


@login_required
def matches(request):
    # Get all matches by user
    picks = Pick.objects.get_all_matches_by_user(request.user)
    # Sort picks by event date
    picks = sorted(picks.items(), key=lambda pick: pick[0].startDateTime)
    context = {'pick_map': picks}

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


@login_required
def myevents(request):


    #groupparticipants = EventParticipant.objects.filter(user=request.user)
    #eventgroups = EventGroup.objects.filter(eventparticipant__in=groupparticipants)
    #events = Event.objects.filter(eventgroup__in=eventgroups)

    events = Event.objects.get_all_by_user(request.user)
    context = {
        'events': events,
        'test': "My Events Page",
    }

    return render(request, 'web/myevents.html', context)


def terms_of_use(request):
    context = {
        'test': "Terms of Use Page",
    }

    return render(request, 'web/termsofuse.html', context)


def how_it_works(request):
    context = {
        'test': "How It Works Page",
    }

    return render(request, 'web/howitworks.html', context)


def privacy_policy(request):
    context = {
        'test': "Privacy Policy Page",
    }

    return render(request, 'web/privacypolicy.html', context)


@login_required
def create_or_update_memo(request, about_user_id):
    if request.method == 'POST':
        # Get content from the body
        content = request.body.decode('utf-8')
        memo = Memo.objects.create_or_update_memo_by_id(request.user, about_user_id, content)

        return JsonResponse({'owner': str(memo.owner), 'about': str(memo.about), 'content': str(memo.content)})
