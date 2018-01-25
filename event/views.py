import base64
import io
import logging
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_time
from formtools.wizard.views import SessionWizardView
from stripe import CardError

from money.billing_logic import get_product_by_event_size, get_price_by_user, pay_for_event
from money.model_transaction import Transaction
from money.models import UserPaymentInfo
from .forms import CreateEventStep1, CreateEventStep2, CreateEventStep3, CreateEventStep4a, \
    CreateEventStep4b, CreateEventStep5, CreateEventStep6
from .models import Event, EventGroup, EventParticipant

# Get an instance of a logger
LOGGER = logging.getLogger(__name__)


# Return a value from a tuple list by key
def get_value(tuples, key):
    dictionary = dict(tuples)
    if key in dictionary:
        return dictionary[key]

    return ''


def view(request, event_id):
    # Fetch the event by ID
    selected_event = get_object_or_404(Event, pk=event_id)

    display_price = float(get_price_by_user(request.user, selected_event)) / 100
    can_leave = False
    can_join = False

    # Get group info
    event_groups = list(selected_event.eventgroup_set.all())
    group1 = event_groups[0]
    group2 = None
    if selected_event.numGroups == 2:
        group2 = event_groups[1]

    # First group info
    group1_participants = group1.get_registered_participants_accounts()
    group1_filled_count = group1_participants.count()
    group1_filled_percentage = round(float(group1_filled_count) / selected_event.maxParticipantsInGroup * 100)
    group1_can_join = False

    # Second group info
    group2_participants = []
    group2_filled_percentage = 0
    group2_filled_count = 0
    group2_can_join = False
    if selected_event.numGroups == 2:
        group2_participants = group2.get_registered_participants_accounts()
        group2_filled_count = group2_participants.count()
        group2_filled_percentage = round(float(group2_filled_count) / selected_event.maxParticipantsInGroup * 100)

    # Check if user can join each group and leave event
    if request.user.is_authenticated and request.user is not None:
        try:
            can_leave = selected_event.can_user_leave(request.user)
        except Exception:
            can_leave = False

        try:
            group1_can_join = group1.can_user_register(request.user)
            can_join = True
        except Exception:
            group1_can_join = False

        if selected_event.numGroups == 2:
            try:
                group2_can_join = group2.can_user_register(request.user)
                can_join = True
            except Exception:
                group2_can_join = False

    context = {
        'event': selected_event,
        'group1': group1,
        'group2': group2,
        'group1_filled_percentage': group1_filled_percentage,
        'group2_filled_percentage': group2_filled_percentage,
        'group1_filled_count': group1_filled_count,
        'group2_filled_count': group2_filled_count,
        'group1_participants': group1_participants,
        'group2_participants': group2_participants,
        'group1_can_join': group1_can_join,
        'group2_can_join': group2_can_join,
        'display_price': display_price,
        'can_join': can_join,
        'can_leave': can_leave
    }

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

            start_date = all_data.get('date')
            start_time = all_data.get('time')
            start_time = parse_time(start_time)
            start_date_time = datetime.combine(start_date, start_time)
            start_date_time = timezone.get_current_timezone().localize(start_date_time)
            all_data.update({'start_date_time': start_date_time})

            # Convert certain values into display format
            all_data.update({'displayType': get_value(Event.TYPES, int(all_data.get('type')))})

            if all_data.get('numGroups') == 1:
                all_data.update({'displayNumParticipants': int(all_data.get('eventSize')) / 2 + 1})
                all_data.update({'displayDuration': int(all_data.get('eventSize')) * 3})
                all_data.update({'displayNumParticipantsPerGroup': int(all_data.get('eventSize')) / 2 + 1})

                display_sexual_identity1 = get_value(EventGroup.IDENTITY_CHOICES, all_data.get('sexualIdentity'))
                if all_data.get('sexualIdentity') == 'other':
                    display_sexual_identity1 = all_data.get('sexualIdentityOther')
                all_data.update({'displaySexualIdentity1': display_sexual_identity1})
                all_data.update({'ageMin1': all_data.get('ageMin')})
                all_data.update({'ageMax1': all_data.get('ageMax')})
            elif all_data.get('numGroups') == 2:
                all_data.update({'displayNumParticipants': int(all_data.get('eventSize'))})
                all_data.update({'displayDuration': int(all_data.get('eventSize')) * 3})
                all_data.update({'displayNumParticipantsPerGroup': int(all_data.get('eventSize')) / 2})

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
        start_date_time = timezone.get_current_timezone().localize(start_date_time)

        lat = all_data.get('cityLat')
        lng = all_data.get('cityLng')
        point = Point(x=0, y=0, srid=4326)

        if lat and lng:
            point.x = lng
            point.y = lat

        num_participants = 0
        if all_data.get('numGroups') == 1:
            num_participants = int(all_data.get('eventSize')) / 2 + 1
        elif all_data.get('numGroups') == 2:
            num_participants = int(all_data.get('eventSize')) / 2

        product = get_product_by_event_size(int(all_data.get('eventSize')))

        event = Event(
            creator=self.request.user,
            name=all_data.get('name'),
            type=all_data.get('type'),
            size=all_data.get('eventSize'),
            startDateTime=start_date_time,
            locationName=all_data.get('locationName'),
            locationCoordinates=point,
            divisionCode=all_data.get('division'),
            countryCode=all_data.get('country'),
            description=all_data.get('description'),
            numGroups=all_data.get('numGroups'),
            maxParticipantsInGroup=num_participants,
            product=product
        )
        event.save()

        # Add photo
        if all_data.get('image_data') and len(all_data.get('image_data')) > 0:
            img_format, img_data = all_data.get('image_data').split(';base64,')
            byte_stream = io.BytesIO(base64.b64decode(img_data))
            event.add_photo(byte_stream, 800)

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
        else:
            group1 = EventGroup(
                event=event,
                sexualIdentity=all_data.get('sexualIdentity1'),
                sexualIdentityOther=all_data.get('sexualIdentityOther1'),
                ageMin=all_data.get('ageMin1'),
                ageMax=all_data.get('ageMax1')
            )
            group1.save()

            group2 = EventGroup(
                event=event,
                sexualIdentity=all_data.get('sexualIdentity2'),
                sexualIdentityOther=all_data.get('sexualIdentityOther2'),
                ageMin=all_data.get('ageMin2'),
                ageMax=all_data.get('ageMax2')
            )
            group2.save()

        messages.add_message(self.request, messages.SUCCESS,
                             'Congratulations, your new event is scheduled! Don\'t forget to register yourself.')

        return HttpResponseRedirect(reverse('event:view', kwargs={'event_id': event.id}))


@login_required
def join(request, group_id):
    current_user = request.user
    selected_group = get_object_or_404(EventGroup, pk=group_id)
    selected_event = selected_group.event

    # Retrieve the payment information for the user
    credit_card = UserPaymentInfo.objects.find_credit_card_by_user(current_user)

    event_price = get_price_by_user(current_user, selected_event)

    # Get credit for the user
    site_credit = Transaction.objects.get_credit_for_user(current_user)
    site_credit_remaining = 0
    if site_credit > event_price:
        site_credit_remaining = site_credit - event_price
        site_credit = event_price

    total_price = event_price - site_credit
    if total_price < 0:
        total_price = 0

    is_free = total_price == 0

    is_creator = current_user == selected_event.creator

    if request.method == 'POST':
        # Check if Stripe token is present and update the saved card
        if 'stripeToken' in request.POST:
            token = request.POST['stripeToken']
            try:
                credit_card = UserPaymentInfo.objects.create_or_update_credit_card(current_user, token)
            except CardError as ce:
                body = ce.json_body
                err = body.get('error', {})

                LOGGER.error(err.get('message'))
                # Refund credit if applicable
                Transaction.objects.refund_credit_used_for_event(current_user, selected_event)
                messages.add_message(request, messages.ERROR, 'Yor card was declined for the following reason: '
                                     + str(err.get('message')))
                return HttpResponseRedirect(reverse('event:join', kwargs={'group_id': group_id}))
            except Exception as e:
                LOGGER.error(e)
                # Refund credit if applicable
                Transaction.objects.refund_credit_used_for_event(current_user, selected_event)
                messages.add_message(request, messages.ERROR, str(e))
                return HttpResponseRedirect(reverse('event:join', kwargs={'group_id': group_id}))

        # Check that credit card exists
        if not credit_card and not is_free:
            messages.add_message(request, messages.ERROR, 'You do not have a credit card on file')
            return HttpResponseRedirect(reverse('event:join', kwargs={'group_id': group_id}))

        # Attempt to add the user to the group
        try:
            participant = selected_group.add_participant(current_user)

            if site_credit > 0:
                # Subtract amount from the credit
                transaction = Transaction(
                    transactionType=Transaction.SITE_CREDIT,
                    user=current_user,
                    amount=0 - site_credit,
                    description='Credit used for event registration',
                    event=selected_event)
                transaction.save()

            # When joining a confirmed event, make a payment
            if selected_event.stage == Event.CONFIRMED:
                pay_for_event(participant, selected_event)

            request.session['joined_group'] = group_id
            return HttpResponseRedirect(reverse('event:join_confirmation'))
        except Exception as e:
            # Refund credit if applicable
            Transaction.objects.refund_credit_used_for_event(current_user, selected_event)
            messages.add_message(request, messages.ERROR, str(e))
            return HttpResponseRedirect(reverse('event:join', kwargs={'group_id': group_id}))

    context = {
        'event': selected_event,
        'group': selected_group,
        'credit_card': credit_card,
        'stripe_secret': settings.STRIPE_SECRET,
        'is_free': is_free,
        'is_creator': is_creator,
        'event_price': float(event_price) / 100,
        'site_credit': float(site_credit) / 100,
        'site_credit_remaining': float(site_credit_remaining) / 100,
        'total_price': float(total_price) / 100
    }

    # Check if user is able to join the group
    try:
        selected_group.can_user_register(current_user)
        # TODO: Check schedule for conflicts
    except Exception as e:
        messages.add_message(request, messages.ERROR, str(e))
        return HttpResponseRedirect(reverse('event:view', kwargs={'event_id': selected_event.id}))

    return render(request, 'event/join.html', context)


@login_required
def join_confirmation(request):
    group_id = request.session.get('joined_group', None)

    if group_id is None:
        messages.add_message(request, messages.ERROR, 'We encountered an error, please try again.')
        return render(request, 'event/join_confirmation.html')

    current_user = request.user
    selected_group = get_object_or_404(EventGroup, pk=group_id)
    selected_event = selected_group.event

    event_price = get_price_by_user(current_user, selected_event)

    # Get credit for the user
    site_credit = Transaction.objects.get_credit_used_for_event(current_user, selected_event)
    expected_revenue = event_price + site_credit

    context = {
        'group': selected_group,
        'event': selected_event,
        'expected_revenue': float(expected_revenue) / 100
    }
    return render(request, 'event/join_confirmation.html', context)


@login_required
def leave(request, event_id):
    current_user = request.user
    selected_event = get_object_or_404(Event, pk=event_id)

    # Can user leave the event?
    try:
        selected_event.can_user_leave(current_user)

        if request.method == 'POST':
            # Mark the participant as left
            participant = EventParticipant.objects.get(user=current_user, group__in=selected_event.eventgroup_set.all(),
                                                       status=EventParticipant.REGISTERED)
            participant.status = EventParticipant.LEFT
            participant.save()

            # Refund the credit if applicable
            refund = Transaction.objects.refund_credit_used_for_event(current_user, selected_event)

            request.session['left_event'] = event_id
            request.session['refund'] = refund
            return HttpResponseRedirect(reverse('event:leave_confirmation'))
    except Exception as e:
        messages.add_message(request, messages.ERROR, str(e))
        return HttpResponseRedirect(reverse('event:view', kwargs={'event_id': event_id}))

    context = {
        'event': selected_event
    }

    return render(request, 'event/leave.html', context)


@login_required
def leave_confirmation(request):
    event_id = request.session.get('left_event', None)
    refund = request.session.get('refund', None)

    if event_id is None or refund is None:
        messages.add_message(request, messages.ERROR, 'We encountered an error, please try again.')
        return render(request, 'event/leave_confirmation.html')

    selected_event = get_object_or_404(Event, pk=event_id)

    context = {
        'event': selected_event,
        'refund': float(refund) / 100
    }

    return render(request, 'event/leave_confirmation.html', context)
