import stripe
import logging

STRIPE_TEST_KEY = "sk_test_28uxXqhjVInC6y28EXbq84je"
LOGGER = logging.getLogger(__name__)


# Retrieve a Stripe Customer by Stripe id
def retrieve_customer(stripe_id):
    stripe.api_key = STRIPE_TEST_KEY

    try:
        customer = stripe.Customer.retrieve(stripe_id)
        LOGGER.info("Stripe customer retrieved: {}".format(customer.id))
        return customer
    except stripe.error.InvalidRequestError:
        return None


# Create a Stripe Customer for later use, returns Stripe id
def create_customer(stripe_token, user_id, user_name, user_email):
    stripe.api_key = STRIPE_TEST_KEY

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
    stripe.api_key = STRIPE_TEST_KEY

    try:
        customer = stripe.Customer.retrieve(stripe_id)
        card = customer.sources.create(source=stripe_token)
        return card
    except stripe.error.InvalidRequestError:
        return None


# Delete a card from customer's record
def delete_card(stripe_id, stripe_card_id):
    stripe.api_key = STRIPE_TEST_KEY

    try:
        LOGGER.info("Stripe deleting card with id {} for customer with id {}".format(stripe_card_id, stripe_id))
        customer = stripe.Customer.retrieve(stripe_id)
        response = customer.sources.retrieve(stripe_card_id).delete()
        return response.deleted
    except stripe.error.InvalidRequestError:
        return False


# Charge a customer by Stripe ID.
# Amount is in cents
def create_charge(amount, currency, description, stripe_id):
    stripe.api_key = STRIPE_TEST_KEY

    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            description=description,
            customer=stripe_id,
        )
        LOGGER.info("Stripe charge created: {}".format(charge.id))
        pass
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        body = e.json_body
        err = body['error']

        LOGGER.error("Status is: {}".format(e.http_status))
        LOGGER.error("Type is: {}".format(err['type']))
        LOGGER.error("Code is: {}".format(err['code']))
        LOGGER.error("Param is: {}".format(err['param']))
        LOGGER.error("Message is: {}".format(err['message']))
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        pass
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        pass
