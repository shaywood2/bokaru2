import logging

from django.conf import settings
from django.utils import timezone

from chat.utils import generate_conversations
from event.models import Event, EventParticipant
from money.models import UserPaymentInfo
from money.payment_service import create_charge

EVENT_MINIMUM_FILL_PERCENTAGE = settings.EVENT_MINIMUM_FILL_PERCENTAGE

LOGGER = logging.getLogger(__name__)


def activate_events():
    # Select all events that start within 1 hour
    end_time = timezone.now() + timezone.timedelta(hours=1)
    events = Event.objects.filter(startDateTime__lte=end_time, stage=Event.CONFIRMED, deleted=False)

    result = []

    for event in events:
        LOGGER.info('Generating conversations for event: {}'.format(str(event)))
        generate_conversations(event)
        event.stage = Event.IN_PROGRESS
        event.save()

        result.append(
            {
                'id': event.id,
                'name': event.name,
                'startTime': event.startDateTime,
                'stage': event.stage,
                'numberOfParticipants': event.numberOfParticipants
            }
        )

        # TODO: send email reminders

    return result


def process_payments():
    # Select all events that start within 24 hours
    end_time = timezone.now() + timezone.timedelta(hours=24)
    events = Event.objects.filter(startDateTime__lte=end_time, stage=Event.REGISTRATION_OPEN, deleted=False)

    for event in events:
        LOGGER.info('Collecting payments for event: {}'.format(str(event)))
        # Check if there are enough participants (over 80%)
        if event.filledPercentage >= EVENT_MINIMUM_FILL_PERCENTAGE:
            # Get event product
            product = event.product
            if not product:
                # TODO: no product, record error
                pass

            # Get all participants
            participants = EventParticipant.objects.filter(group__in=event.eventgroup_set.all(),
                                                           status=EventParticipant.REGISTERED)

            for participant in participants:
                try:
                    payment_info = UserPaymentInfo.objects.get(user=participant.user)
                    stripe_id = payment_info.stripe_customer_id
                    if not stripe_id:
                        # TODO: missing stripe id, record error
                        pass

                    # Create a charge
                    # TODO: record success or failure
                    create_charge(product.amount, 'CAD', str(event), stripe_id)
                    participant.status = EventParticipant.PAYMENT_SUCCESS
                    participant.save()
                    # TODO: send confirmation email
                except UserPaymentInfo.DoesNotExist:
                    # TODO: missing payment info, record error
                    pass
        else:
            # Not enough participants, cancel the event

            # Get all participants
            participants = EventParticipant.objects.filter(group__in=event.eventgroup_set.all(),
                                                           status=EventParticipant.REGISTERED)
            for participant in participants:
                # TODO: send cancellation emails
                pass
