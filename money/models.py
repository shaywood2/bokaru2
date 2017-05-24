from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class UserPaymentInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user))
    stripe_customer_id = models.CharField(max_length=150, blank=True)
    credit_card_id = models.CharField(max_length=150, blank=True)
    credit_card_brand = models.CharField(max_length=20, blank=True)
    credit_card_last_4 = models.CharField(max_length=10, blank=True)
    credit_card_exp_month = models.SmallIntegerField(blank=True)
    credit_card_exp_year = models.SmallIntegerField(blank=True)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' [' + self.stripe_customer_id + ']'

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
