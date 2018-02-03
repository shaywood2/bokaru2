import logging

from django.utils import timezone

from bokaru.email import send_email
from chat.utils import generate_conversations
from event.models import Event, EventParticipant
from money.billing_logic import pay_for_event
from money.model_transaction import Transaction
from money.payment_service import CardDeclinedException

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

            # Send email reminders
            participants = EventParticipant.objects.filter(group__in=event.eventgroup_set.all(),
                                                           status__in=[EventParticipant.REGISTERED,
                                                                       EventParticipant.PAYMENT_SUCCESS])
            for participant in participants:
                email_data = {
                    'event_name': event.name,
                    'event_start_time': event.startDateTime
                }

                send_email(participant.user.email, email_data, 'event_starting')

        except Exception as e:
            LOGGER.error('Failed to generate conversations for event {:d}. Error message: {!s}'.format(event.id, e))

            # TODO: cancel the event here? Users will have a bad time

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

    LOGGER.info('Processing payments @ {}. Found {} events to process.'.format(str(now), str(len(events))))

    result = []

    for event in events:
        try:
            LOGGER.info('Processing payments for event: {:d}'.format(event.id))

            if event.can_be_activated():
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
                        # Send a reminder email
                        email_data = {
                            'username': participant.user.username,
                            'event_name': event.name,
                            'event_start_time': event.startDateTime,
                            'event_id': event.id
                        }

                        send_email(participant.user.email, email_data, 'event_upcoming')
                    except CardDeclinedException as cde:
                        # TODO: send an error message https://stripe.com/docs/declines/codes
                        # Send card declined email
                        email_data = {
                            'username': participant.user.username,
                            'event_name': event.name,
                            'event_start_time': event.startDateTime,
                            'event_id': event.id
                        }

                        send_email(participant.user.email, email_data, 'payment_failure')
                    except Exception as e:
                        # Send payment failed email
                        email_data = {
                            'username': participant.user.username,
                            'event_name': event.name,
                            'event_start_time': event.startDateTime,
                            'event_id': event.id
                        }

                        send_email(participant.user.email, email_data, 'payment_failure')

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
                    # Send cancellation emails

                    email_data = {
                        'username': participant.user.username,
                        'event_name': event.name,
                        'event_start_time': event.startDateTime,
                        'event_id': event.id
                    }

                    send_email(participant.user.email, email_data, 'event_cancelled')

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
