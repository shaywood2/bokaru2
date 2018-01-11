import logging

import stripe
from django.conf import settings

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


class CardDeclinedException(Exception):
    def __init__(self, status, ex_type, code, param, message):
        self.status = status
        self.ex_type = ex_type
        self.code = code
        self.param = param
        self.message = message
