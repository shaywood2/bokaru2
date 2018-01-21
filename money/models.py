from django.conf import settings
from django.db import models

from .payment_service import create_customer, delete_card, create_card


class PaymentInfoManager(models.Manager):
    # Create or update a credit card in Stripe and save the result
    def create_or_update_credit_card(self, owner_user, stripe_token):
        try:
            # Retrieve the payment information for the user
            payment_info = self.get(user=owner_user)

            # Delete existing credit card
            if payment_info.credit_card_id != 0:
                delete_card(payment_info.stripe_customer_id, payment_info.credit_card_id)

            # Create a card for an existing Customer
            credit_card = create_card(payment_info.stripe_customer_id, stripe_token)
            # TODO: handle card creation errors
            # Store the payment info
            payment_info.credit_card_id = credit_card.id
            payment_info.credit_card_brand = credit_card.brand
            payment_info.credit_card_last_4 = credit_card.last4
            payment_info.credit_card_exp_month = credit_card.exp_month
            payment_info.credit_card_exp_year = credit_card.exp_year
            payment_info.save()
            return {
                'brand': payment_info.credit_card_brand,
                'last4': payment_info.credit_card_last_4,
                'exp_month': payment_info.credit_card_exp_month,
                'exp_year': payment_info.credit_card_exp_year,
                'id': payment_info.credit_card_id,
            }
        except UserPaymentInfo.DoesNotExist:
            # Create a Customer with a credit card
            stripe_customer = create_customer(stripe_token, owner_user.id, owner_user.first_name + ' '
                                              + owner_user.last_name, owner_user.email)

            credit_card = stripe_customer.sources.data[0]

            # Store the payment info
            payment_info = self.create(
                user=owner_user,
                stripe_customer_id=stripe_customer.id,
                credit_card_id=credit_card.id,
                credit_card_brand=credit_card.brand,
                credit_card_last_4=credit_card.last4,
                credit_card_exp_month=credit_card.exp_month,
                credit_card_exp_year=credit_card.exp_year
            )
            return {
                'brand': payment_info.credit_card_brand,
                'last4': payment_info.credit_card_last_4,
                'exp_month': payment_info.credit_card_exp_month,
                'exp_year': payment_info.credit_card_exp_year,
                'id': payment_info.credit_card_id,
            }

    # Find credit card info by user
    def find_credit_card_by_user(self, user):
        try:
            payment_info = self.get(user=user)

            # Get the saved credit card
            if payment_info.has_card():
                return {
                    'brand': payment_info.credit_card_brand,
                    'last4': payment_info.credit_card_last_4,
                    'exp_month': payment_info.credit_card_exp_month,
                    'exp_year': payment_info.credit_card_exp_year,
                    'id': payment_info.credit_card_id,
                }
            else:
                return None
        except UserPaymentInfo.DoesNotExist:
            return None

    # Find credit card info by user
    def find_stripe_id_by_user(self, user):
        try:
            payment_info = self.get(user=user)

            return payment_info.stripe_customer_id
        except UserPaymentInfo.DoesNotExist:
            return None


class UserPaymentInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    stripe_customer_id = models.CharField(max_length=150, blank=True)
    credit_card_id = models.CharField(max_length=150, blank=True)
    credit_card_brand = models.CharField(max_length=20, blank=True)
    credit_card_last_4 = models.CharField(max_length=10, blank=True)
    credit_card_exp_month = models.SmallIntegerField(blank=True)
    credit_card_exp_year = models.SmallIntegerField(blank=True)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = PaymentInfoManager()

    def __str__(self):
        return self.user.username + ' [Stripe id: ' + self.stripe_customer_id + ']'

    # Check if the user has a card ID
    def has_card(self):
        return self.credit_card_id is not None and len(self.credit_card_id) > 0

    # Delete all card information
    def delete_card(self):
        self.credit_card_id = ''
        self.credit_card_brand = ''
        self.credit_card_last_4 = ''
        self.credit_card_exp_month = 0
        self.credit_card_exp_year = 0
        self.save()


class Product(models.Model):
    name = models.CharField(max_length=150)
    short_code = models.CharField(max_length=50)
    description = models.CharField(max_length=150, blank=True)
    amount = models.IntegerField()  # Price in cents

    def __str__(self):
        return self.name + ' [' + self.short_code + '], ' + str(self.amount)
