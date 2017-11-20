import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404

from account.models import Account
from money.billing_logic import get_product_by_participant_number
from .forms import EventForm, EventGroupForm
from .models import Event, EventGroup

# Get an instance of a logger
logger = logging.getLogger(__name__)


def view(request, event_id):
    selected_event = get_object_or_404(Event, pk=event_id)
    event_groups = list(selected_event.eventgroup_set.all())

    # First group info
    group1_filled_percentage = float(
        event_groups[0].count_registered_participants()) / selected_event.maxParticipantsInGroup * 100
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
        group2_filled_percentage = float(
            event_groups[1].count_registered_participants()) / selected_event.maxParticipantsInGroup * 100
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
def create(request):
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


@login_required
def join(request, group_id):
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


@login_required
def payment(request):
    context = {
        'test': "Event Pay Page",
    }

    return render(request, 'web/payment.html', context)
