import logging

import stripe
from django.conf import settings

from event.models import EventParticipant
from money.models import UserPaymentInfo

STRIPE_KEY = settings.STRIPE_KEY

LOGGER = logging.getLogger(__name__)


# Retrieve a Stripe Customer by Stripe id
def retrieve_customer(stripe_id):
    stripe.api_key = STRIPE_KEY

    try:
        customer = stripe.Customer.retrieve(stripe_id)
        LOGGER.info("Stripe customer retrieved: {}".format(customer.id))
        return customer
    except stripe.error.InvalidRequestError:
        return None


# Create a Stripe Customer for later use, returns Stripe id
def create_customer(stripe_token, user_id, user_name, user_email):
    stripe.api_key = STRIPE_KEY

    customer = stripe.Customer.create(
        source=stripe_token,
        description=user_name,
        email=user_email,
        metadata={'user_id': user_id}
    )
    LOGGER.info("Stripe customer created: {}".format(customer.id))
    return customer


# Create a card for the given customer
def create_card(stripe_id, stripe_token):
    stripe.api_key = STRIPE_KEY

    try:
        customer = stripe.Customer.retrieve(stripe_id)
        card = customer.sources.create(source=stripe_token)
        return card
    except stripe.error.InvalidRequestError:
        return None


# Delete a card from customer's record
def delete_card(stripe_id, stripe_card_id):
    stripe.api_key = STRIPE_KEY

    try:
        LOGGER.info("Stripe deleting card with id {} for customer with id {}".format(stripe_card_id, stripe_id))
        customer = stripe.Customer.retrieve(stripe_id)
        response = customer.sources.retrieve(stripe_card_id).delete()
        return response.deleted
    except stripe.error.InvalidRequestError:
        return False


# Charge a customer by Stripe ID.
# Amount is in cents
def create_charge(amount, currency, user_id, event_id, stripe_id):
    stripe.api_key = STRIPE_KEY

    charge = stripe.Charge.create(
        amount=amount,
        currency=currency,
        description='Charge for event ' + str(event_id),
        metadata={'user_id': user_id, 'event_id': event_id},
        customer=stripe_id
    )
    LOGGER.info("Stripe charge created: {}".format(charge.id))
    pass


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


class CardDeclinedException(Exception):
    def __init__(self, status, ex_type, code, param, message):
        self.status = status
        self.ex_type = ex_type
        self.code = code
        self.param = param
        self.message = message
