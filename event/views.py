import base64
import io
import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from django.utils.dateparse import parse_time
from formtools.wizard.views import SessionWizardView

from money.billing_logic import get_product_by_participant_number
from .forms import CreateEventStep1, CreateEventStep2, CreateEventStep3, CreateEventStep4a, \
    CreateEventStep4b, CreateEventStep5, CreateEventStep6
from .models import Event, EventGroup

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Return a value from a tuple list by key
def get_value(tuples, key):
    dictionary = dict(tuples)
    if key in dictionary:
        return dictionary[key]

    return ''


def view(request, event_id):
    # Fetch the event by ID
    selected_event = get_object_or_404(Event, pk=event_id)
    # Convert certain values into display format
    display_type = get_value(Event.TYPES, selected_event.type)
    display_num_participants = None
    display_duration = None
    num_groups = selected_event.numGroups
    if num_groups == 1:
        display_num_participants = selected_event.maxParticipantsInGroup
        display_duration = (selected_event.maxParticipantsInGroup - 1) * 6
    elif num_groups == 2:
        display_num_participants = selected_event.maxParticipantsInGroup * 2
        display_duration = selected_event.maxParticipantsInGroup * 6

    # Get group info
    event_groups = list(selected_event.eventgroup_set.all())
    group1 = event_groups[0]
    group2 = None
    if num_groups == 2:
        group2 = event_groups[1]

    # First group info
    group1_participants = group1.get_registered_participants_accounts()
    group1_filled_percentage = float(group1_participants.count()) / selected_event.maxParticipantsInGroup * 100
    group1_spots_left = selected_event.maxParticipantsInGroup - group1_participants.count()
    group1_can_join = False

    # Second group info
    group2_participants = []
    group2_filled_percentage = 0
    group2_spots_left = 0
    group2_can_join = False
    if group2:
        group2_participants = group2.get_registered_participants_accounts()
        group2_filled_percentage = float(
            group2_participants.count()) / selected_event.maxParticipantsInGroup * 100
        group2_spots_left = selected_event.maxParticipantsInGroup - group2_participants.count()

    # Check if user is registered
    is_registered = False
    if request.user.is_authenticated() and request.user is not None:
        is_registered = selected_event.is_registered(request.user)

    context = {
        'event': selected_event,
        'group1': group1,
        'group2': group2,
        'num_groups': num_groups,
        'group1_filled_percentage': group1_filled_percentage,
        'group2_filled_percentage': group2_filled_percentage,
        'group1_spots_left': group1_spots_left,
        'group2_spots_left': group2_spots_left,
        'group1_participants': group1_participants,
        'group2_participants': group2_participants,
        'is_registered': is_registered,
        'group1_can_join': group1_can_join,
        'group2_can_join': group2_can_join,
        'displayType': display_type,
        'displayNumParticipants': display_num_participants,
        'displayDuration': display_duration
    }

    # event.update({'displayTime': get_value(CreateEventStep1.TIME_CHOICES, all_data.get('time'))})

    return render(request, 'event/view.html', context)


class CreateEventWizard(SessionWizardView):
    FORMS = [
        ('step1', CreateEventStep1),
        ('step2', CreateEventStep2),
        ('step3', CreateEventStep3),
        ('step4a', CreateEventStep4a),
        ('step4b', CreateEventStep4b),
        ('step5', CreateEventStep5),
        ('step6', CreateEventStep6)
    ]

    TEMPLATES = {
        'step1': 'event/create/step1.html',
        'step2': 'event/create/step2.html',
        'step3': 'event/create/step3.html',
        'step4a': 'event/create/step4a.html',
        'step4b': 'event/create/step4b.html',
        'step5': 'event/create/step5.html',
        'step6': 'event/create/step6.html'
    }

    form_list = FORMS

    def showStep4a(self):
        cleaned_data = self.get_cleaned_data_for_step('step3') or {}
        if cleaned_data.get('numGroups') == 1:
            return True
        else:
            return False

    def showStep4b(self):
        cleaned_data = self.get_cleaned_data_for_step('step3') or {}
        if cleaned_data.get('numGroups') == 2:
            return True
        else:
            return False

    condition_dict = {'step4a': showStep4a, 'step4b': showStep4b}

    def get_template_names(self):
        return [CreateEventWizard.TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(CreateEventWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'step6':
            all_data = self.get_all_cleaned_data()
            # Convert certain values into display format
            all_data.update({'displayTime': get_value(CreateEventStep1.TIME_CHOICES, all_data.get('time'))})
            all_data.update({'displayType': get_value(Event.TYPES, int(all_data.get('type')))})

            if all_data.get('numGroups') == 1:
                all_data.update({'displayNumParticipants': int(all_data.get('eventSize')) / 2 + 1})
                all_data.update({'displayDuration': int(all_data.get('eventSize')) * 3})
                all_data.update({'displaySpotsLeft': int(all_data.get('eventSize')) / 2 + 1})

                display_sexual_identity1 = get_value(EventGroup.IDENTITY_CHOICES, all_data.get('sexualIdentity'))
                if all_data.get('sexualIdentity') == 'other':
                    display_sexual_identity1 = all_data.get('sexualIdentityOther')
                all_data.update({'displaySexualIdentity1': display_sexual_identity1})
                all_data.update({'ageMin1': all_data.get('ageMin')})
                all_data.update({'ageMax1': all_data.get('ageMax')})
            elif all_data.get('numGroups') == 2:
                all_data.update({'displayNumParticipants': int(all_data.get('eventSize'))})
                all_data.update({'displayDuration': int(all_data.get('eventSize')) * 3})
                all_data.update({'displaySpotsLeft': int(all_data.get('eventSize')) / 2})

                display_sexual_identity1 = get_value(EventGroup.IDENTITY_CHOICES, all_data.get('sexualIdentity1'))
                if all_data.get('sexualIdentity1') == 'other':
                    display_sexual_identity1 = all_data.get('sexualIdentityOther1')
                all_data.update({'displaySexualIdentity1': display_sexual_identity1})
                display_sexual_identity2 = get_value(EventGroup.IDENTITY_CHOICES, all_data.get('sexualIdentity2'))
                if all_data.get('sexualIdentity2') == 'other':
                    display_sexual_identity2 = all_data.get('sexualIdentityOther2')
                all_data.update({'displaySexualIdentity2': display_sexual_identity2})
            context.update({'all_data': all_data})
        return context

    def done(self, form_list, **kwargs):
        # Save the event
        all_data = self.get_all_cleaned_data()

        start_date = all_data.get('date')
        start_time = all_data.get('time')
        start_time = parse_time(start_time)
        start_date_time = datetime.combine(start_date, start_time)
        # TODO: figure out the timezone as well

        logger.info('startDateTime ' + str(start_date_time))

        lat = all_data.get('cityLat')
        lng = all_data.get('cityLng')
        point = Point(x=0, y=0, srid=4326)

        if lat and lng:
            point.set_x(lat)
            point.set_y(lng)

        num_participants = 0
        if all_data.get('numGroups') == 1:
            num_participants = int(all_data.get('eventSize')) / 2 + 1
        elif all_data.get('numGroups') == 2:
            num_participants = int(all_data.get('eventSize')) / 2

        product = get_product_by_participant_number(int(all_data.get('eventSize')))

        event = Event(
            creator=self.request.user,
            name=all_data.get('name'),
            type=all_data.get('type'),
            startDateTime=start_date_time,
            locationName=all_data.get('locationName'),
            locationCoordinates=point,
            description=all_data.get('description'),
            numGroups=all_data.get('numGroups'),
            maxParticipantsInGroup=num_participants,
            product=product
        )
        event.save()

        logger.info('saved event ' + str(event.id))

        # Add photo
        if all_data.get('image_data') and len(all_data.get('image_data')) > 0:
            img_format, img_data = all_data.get('image_data').split(';base64,')
            byte_stream = io.BytesIO(base64.b64decode(img_data))

            event.add_photo(byte_stream, 800)

            logger.info('saved photo')

        # Save event groups
        if all_data.get('numGroups') == 1:
            group = EventGroup(
                event=event,
                sexualIdentity=all_data.get('sexualIdentity'),
                sexualIdentityOther=all_data.get('sexualIdentityOther'),
                ageMin=all_data.get('ageMin'),
                ageMax=all_data.get('ageMax')
            )
            group.save()
            logger.info('saved group ' + str(group.id))
        else:
            group1 = EventGroup(
                event=event,
                sexualIdentity=all_data.get('sexualIdentity1'),
                sexualIdentityOther=all_data.get('sexualIdentityOther1'),
                ageMin=all_data.get('ageMin1'),
                ageMax=all_data.get('ageMax1')
            )
            group1.save()
            logger.info('saved group ' + str(group1.id))
            group2 = EventGroup(
                event=event,
                sexualIdentity=all_data.get('sexualIdentity2'),
                sexualIdentityOther=all_data.get('sexualIdentityOther2'),
                ageMin=all_data.get('ageMin2'),
                ageMax=all_data.get('ageMax2')
            )
            group2.save()
            logger.info('saved group ' + str(group2.id))

        return HttpResponseRedirect(reverse('event:view', kwargs={'event_id': event.id}))


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
