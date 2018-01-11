import logging

import stripe

from event.models import EventParticipant
from money.payment_service import create_charge, CardDeclinedException
from .models import Product, UserPaymentInfo

LOGGER = logging.getLogger(__name__)

# Constants, must match product IDs in database
SMALL_EVENT_ID = 'smallevent'
MEDIUM_EVENT_ID = 'mediumevent'
LARGE_EVENT_ID = 'largeevent'


# Return a product based on the number of participants in the event
def get_product_by_participant_number(participant_number):
    try:
        if participant_number <= 10:
            return Product.objects.get(short_code=SMALL_EVENT_ID)
        elif participant_number <= 20:
            return Product.objects.get(short_code=MEDIUM_EVENT_ID)
        else:
            return Product.objects.get(short_code=LARGE_EVENT_ID)

    except Product.DoesNotExist:
        raise Exception('Product was not defined')


# Figure out the amount and create a payment for the specified event
def pay_for_event(participant, event):
    user = participant.user
    product = event.product

    try:
        payment_info = UserPaymentInfo.objects.get(user=user)
        stripe_id = payment_info.stripe_customer_id
    except UserPaymentInfo.DoesNotExist:
        participant.status = EventParticipant.PAYMENT_FAILURE
        participant.save()
        LOGGER.error('UserPaymentInfo not specified')
        raise Exception('UserPaymentInfo not specified')

    if not stripe_id:
        participant.status = EventParticipant.PAYMENT_FAILURE
        participant.save()
        LOGGER.error('Stripe ID not specified')
        raise Exception('Stripe ID not specified')

    # Create a charge
    try:
        create_charge(product.amount, 'cad', user.id, event.id, stripe_id)

        participant.status = EventParticipant.PAYMENT_SUCCESS
        participant.save()
    except stripe.error.CardError as e:
        participant.status = EventParticipant.PAYMENT_FAILURE
        participant.save()

        # In case of a decline, stripe.error.CardError will be caught
        body = e.json_body
        err = body['error']

        LOGGER.error('Failed to create a charge')
        LOGGER.error('Status is: {}'.format(e.http_status))
        LOGGER.error('Type is: {}'.format(err['type']))
        LOGGER.error('Code is: {}'.format(err['code']))
        LOGGER.error('Param is: {}'.format(err['param']))
        LOGGER.error('Message is: {}'.format(err['message']))

        raise CardDeclinedException(e.http_status, err['type'], err['code'], err['param'], err['message'])
    except stripe.error.StripeError as e:
        participant.status = EventParticipant.PAYMENT_FAILURE
        participant.save()

        # Display a very generic error to the user, and maybe send yourself an email
        LOGGER.error('Failed to create a charge')
        raise Exception('Failed to create a charge: {!s}'.format(e))
