from django.conf import settings
from django.db import models

from event.models import EventParticipant, Event, EventGroup


# Return a value from a tuple list by key
def get_value(tuples, key):
    dictionary = dict(tuples)
    if key in dictionary:
        return dictionary[key]

    return ''


class TransactionManager(models.Manager):
    def get_history_for_user(self, user):
        return self.filter(user=user).order_by('-created')

    def get_credit_for_user(self, user):
        result = 0
        credit_transactions = self.filter(user=user, transactionType=Transaction.SITE_CREDIT)

        for credit_transaction in credit_transactions:
            result += credit_transaction.amount

        return result

    def get_credit_used_for_event(self, user, event):
        result = 0
        credit_transactions = self.filter(user=user, transactionType=Transaction.SITE_CREDIT, event=event)

        for credit_transaction in credit_transactions:
            result += credit_transaction.amount

        return result

    def refund_credit_used_for_event(self, user, event):
        credit_used = self.get_credit_used_for_event(user, event)
        if credit_used < 0:
            transaction = Transaction(
                transactionType=Transaction.SITE_CREDIT,
                user=user,
                amount=0 - credit_used,
                description='Refunded credit for event registration',
                event=event)
            transaction.save()

        return 0 - credit_used


class Transaction(models.Model):
    CREDIT_CARD = 1
    SITE_CREDIT = 2

    TYPES = [
        (CREDIT_CARD, 'Credit Card'),
        (SITE_CREDIT, 'Site Credit')
    ]

    transactionType = models.PositiveSmallIntegerField(choices=TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.IntegerField()  # Price in cents
    description = models.CharField(max_length=150, blank=True)
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.PROTECT)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def displayAmount(self):
        return (float(self.amount)) / 100

    objects = TransactionManager()

    def __str__(self):
        return self.user.username + ' | ' + get_value(Transaction.TYPES, self.transactionType) \
               + ' ' + str(self.amount) + ' [' + self.description + ']'
