import logging

from django.conf import settings
from django.utils import timezone

from chat.utils import generate_conversations
from event.models import Event, EventParticipant
from money.billing_logic import pay_for_event
from money.payment_service import CardDeclinedException
from money.model_transaction import Transaction

EVENT_MINIMUM_FILL_PERCENTAGE = settings.EVENT_MINIMUM_FILL_PERCENTAGE

LOGGER = logging.getLogger(__name__)


def activate_events():
    # Select all events that start within 1 hour
    now = timezone.now()
    end_time = timezone.now() + timezone.timedelta(hours=1)
    events = Event.objects.filter(startDateTime__gte=now, startDateTime__lte=end_time,
                                  stage=Event.CONFIRMED, deleted=False)

    result = []

    for event in events:
        try:
            LOGGER.info('Generating conversations for event {:d}.'.format(event.id))
            generate_conversations(event)
            event.stage = Event.IN_PROGRESS
            event.save()

            result.append(
                {
                    'id': event.id,
                    'name': event.name,
                    'startTime': event.startDateTime,
                    'stage': event.stage,
                    'numberOfParticipants': event.numberOfParticipants,
                    'success': True
                }
            )

            # TODO: send email reminders
        except Exception as e:
            LOGGER.error('Failed to generate conversations for event {:d}. Error message: {!s}'.format(event.id, e))

            result.append(
                {
                    'id': event.id,
                    'name': event.name,
                    'startTime': event.startDateTime,
                    'stage': event.stage,
                    'numberOfParticipants': event.numberOfParticipants,
                    'success': False
                }
            )

    return result


def process_payments():
    # Select all events that start within 24 hours
    now = timezone.now()
    end_time = timezone.now() + timezone.timedelta(hours=24)
    events = Event.objects.filter(startDateTime__gte=now, startDateTime__lte=end_time,
                                  stage=Event.REGISTRATION_OPEN, deleted=False)

    result = []

    for event in events:
        try:
            LOGGER.info('Processing payments for event: {:d}'.format(event.id))

            # Check if there are enough participants (over 80%)
            if event.filledPercentage >= EVENT_MINIMUM_FILL_PERCENTAGE:
                # Make sure that product exists
                product = event.product
                if not product:
                    raise Exception('Product not specified')

                # Get all participants
                participants = EventParticipant.objects.filter(group__in=event.eventgroup_set.all(),
                                                               status=EventParticipant.REGISTERED)

                for participant in participants:
                    try:
                        pay_for_event(participant, event)
                        # TODO: send payment successful email
                    except CardDeclinedException as cde:
                        # https://stripe.com/docs/declines/codes
                        # TODO: send card declined email
                        pass
                    except Exception as e:
                        # TODO: send payment failed email
                        pass

                event.stage = Event.CONFIRMED
                event.save()

                result.append(
                    {
                        'id': event.id,
                        'name': event.name,
                        'startTime': event.startDateTime,
                        'stage': event.stage,
                        'numberOfParticipants': event.numberOfParticipants,
                        'success': True
                    }
                )
            else:
                # Not enough participants, cancel the event

                # Get all participants
                participants = EventParticipant.objects.filter(group__in=event.eventgroup_set.all(),
                                                               status=EventParticipant.REGISTERED)
                for participant in participants:
                    # Refund credit if used for event
                    Transaction.objects.refund_credit_used_for_event(participant.user, event)
                    # TODO: send cancellation emails
                    pass

                event.stage = Event.CANCELLED
                event.save()

                result.append(
                    {
                        'id': event.id,
                        'name': event.name,
                        'startTime': event.startDateTime,
                        'stage': event.stage,
                        'numberOfParticipants': event.numberOfParticipants,
                        'success': True
                    }
                )
        except Exception as e:
            LOGGER.error('Failed to process payments for event {:d}. Error message: {!s}'.format(event.id, e))

            # Get all participants
            participants = EventParticipant.objects.filter(group__in=event.eventgroup_set.all(),
                                                           status=EventParticipant.REGISTERED)
            for participant in participants:
                # TODO: send error emails
                pass

            result.append(
                {
                    'id': event.id,
                    'name': event.name,
                    'startTime': event.startDateTime,
                    'stage': event.stage,
                    'numberOfParticipants': event.numberOfParticipants,
                    'success': False
                }
            )

    return result
