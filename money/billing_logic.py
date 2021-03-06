import logging

import stripe
from django.utils import timezone

from bokaru.email import send_email
from event.models import Event, EventParticipant
from money.model_transaction import Transaction
from money.payment_service import create_charge, CardDeclinedException
from .models import Product, UserPaymentInfo

LOGGER = logging.getLogger(__name__)

# Constants, must match product IDs in database
SMALL_EVENT_ID = 'smallevent'
MEDIUM_EVENT_ID = 'mediumevent'
LARGE_EVENT_ID = 'largeevent'


# Return a product based on the number of participants in the event
def get_product_by_event_size(size):
    try:
        if size == Event.SMALL:
            return Product.objects.get(short_code=SMALL_EVENT_ID)
        elif size == Event.MEDIUM:
            return Product.objects.get(short_code=MEDIUM_EVENT_ID)
        elif size == Event.LARGE:
            return Product.objects.get(short_code=LARGE_EVENT_ID)
        else:
            raise Exception('Unknown event size: ' + str(size))

    except Product.DoesNotExist:
        raise Exception('Product was not defined')


# Get the price of the event by specified user
def get_price_by_user(user, event):
    if event.creator == user:
        return 0

    return event.product.amount


# Figure out the amount and create a payment for the specified event
def pay_for_event(participant, event):
    user = participant.user

    event_price = get_price_by_user(user, event)

    # Get credit used for event (negative)
    event_price_discount = Transaction.objects.get_credit_used_for_event(user, event)

    charge_to_card = event_price + event_price_discount

    LOGGER.info('User {!s} is paying for event {!s}. Site credit used: {:d},  credit card charge: {:d}.'
                .format(participant.user, event, event_price_discount, charge_to_card))

    if charge_to_card < 0:
        LOGGER.error('Amount of credit used for event ({:d}) is greater than the event\'s price ({:d}).'
                     ' Event: {!s}. Participant: {!s}'
                     .format(event_price_discount, event_price, event, participant))
        charge_to_card = 0

    if charge_to_card == 0:
        # No need to charge the card
        participant.status = EventParticipant.PAYMENT_SUCCESS
        participant.save()
    else:
        stripe_id = UserPaymentInfo.objects.find_stripe_id_by_user(user)

        if not stripe_id:
            participant.status = EventParticipant.PAYMENT_FAILURE
            participant.save()
            LOGGER.error('Stripe ID not specified')
            raise Exception('Stripe ID not specified')

        # Create a charge
        try:
            charge = create_charge(charge_to_card, 'cad', user.id, event.id, stripe_id)

            # Record the transaction
            transaction = Transaction(
                transactionType=Transaction.CREDIT_CARD,
                transactionReason=Transaction.REASON_EVENT_REGISTRATION_CREDIT_CARD,
                user=user,
                amount=charge_to_card,
                event=event,
                stripe_charge_id=charge.id
            )
            transaction.save()

            participant.status = EventParticipant.PAYMENT_SUCCESS
            participant.save()

            # Email the receipt
            email_data = {
                'event_price': float(event_price) / 100,
                'charge_to_card': float(charge_to_card) / 100,
                'event_price_discount': float(event_price_discount) / 100,
                'event_name': event.name,
                'invoice_id': charge.id,
                'date': timezone.now()
            }

            send_email(participant.user.email, email_data, 'payment_success')

        except stripe.error.CardError as e:
            participant.status = EventParticipant.PAYMENT_FAILURE
            participant.save()

            # In case of a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body['error']

            LOGGER.error('Failed to create a charge. '
                         'Status is: {}. Type is: {}. Code is: {}. Param is: {}. Message is: {}.'
                         .format(e.http_status, err['type'], err['code'], err['param'], err['message']))

            raise CardDeclinedException(e.http_status, err['type'], err['code'], err['param'], err['message'])
        except stripe.error.StripeError as e:
            participant.status = EventParticipant.PAYMENT_FAILURE
            participant.save()

            # Display a very generic error to the user, and maybe send yourself an email
            LOGGER.error('Failed to create a charge: {!s}'.format(e))
            raise Exception('Failed to create a charge: {!s}'.format(e))
