from django.conf import settings
from django.db import models

from event.models import Event

WELCOME_CREDIT_TEXT = getattr(settings, 'WELCOME_CREDIT_TEXT', 'Welcome to the site bonus')
WELCOME_CREDIT_AMOUNT = getattr(settings, 'WELCOME_CREDIT', 0)
CONSOLATION_CREDIT_TEXT = getattr(settings, 'CONSOLATION_CREDIT_TEXT', 'Better luck next time bonus')
CONSOLATION_CREDIT_AMOUNT = getattr(settings, 'CONSOLATION_CREDIT', 0)


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
        credit_transactions = self.filter(user=user,
                                          transactionType=Transaction.SITE_CREDIT,
                                          transactionReason=Transaction.REASON_EVENT_REGISTRATION_SITE_CREDIT,
                                          event=event)

        for credit_transaction in credit_transactions:
            result += credit_transaction.amount

        return result

    def refund_credit_used_for_event(self, user, event):
        credit_used = self.get_credit_used_for_event(user, event)
        if credit_used < 0:
            transaction = Transaction(
                transactionType=Transaction.SITE_CREDIT,
                transactionReason=Transaction.REASON_SITE_CREDIT_REFUND,
                user=user,
                amount=0 - credit_used,
                event=event)
            transaction.save()

        return 0 - credit_used

    @staticmethod
    def apply_welcome_credit(user):
        if WELCOME_CREDIT_AMOUNT > 0:
            transaction = Transaction(
                transactionType=Transaction.SITE_CREDIT,
                transactionReason=Transaction.REASON_JOIN_BONUS,
                user=user,
                amount=WELCOME_CREDIT_AMOUNT)
            transaction.save()

        return WELCOME_CREDIT_AMOUNT

    def apply_consolation_credit(self, user, event):
        if CONSOLATION_CREDIT_AMOUNT > 0:
            try:
                existing_bonus = self.get(user=user,
                                          event=event,
                                          transactionType=Transaction.SITE_CREDIT,
                                          transactionReason=Transaction.REASON_CONSOLATION_BONUS)
                return existing_bonus.amount
            except Transaction.DoesNotExist:
                transaction = Transaction(
                    user=user,
                    event=event,
                    transactionType=Transaction.SITE_CREDIT,
                    transactionReason=Transaction.REASON_CONSOLATION_BONUS,
                    amount=CONSOLATION_CREDIT_AMOUNT)
                transaction.save()

        return CONSOLATION_CREDIT_AMOUNT


class Transaction(models.Model):
    CREDIT_CARD = 1
    SITE_CREDIT = 2
    REFUND = 3
    FAILED_CHARGE = 4

    REASON_EVENT_REGISTRATION_CREDIT_CARD = 1
    REASON_EVENT_REGISTRATION_SITE_CREDIT = 2
    REASON_JOIN_BONUS = 3
    REASON_SITE_CREDIT_REFUND = 4
    REASON_CONSOLATION_BONUS = 5
    REASON_OTHER_BONUS = 6

    TYPES = [
        (CREDIT_CARD, 'Credit Card'),
        (REFUND, 'Refund'),
        (SITE_CREDIT, 'Site Credit'),
        (FAILED_CHARGE, 'Failed Charge')
    ]

    REASONS = [
        (REASON_EVENT_REGISTRATION_CREDIT_CARD, 'Payment for event registration'),
        (REASON_EVENT_REGISTRATION_SITE_CREDIT, 'Credit used for event registration'),
        (REASON_JOIN_BONUS, WELCOME_CREDIT_TEXT),
        (REASON_SITE_CREDIT_REFUND, 'Refunded credit for event registration'),
        (REASON_CONSOLATION_BONUS, 'Better luck next time bonus'),
        (REASON_OTHER_BONUS, 'Site credit')
    ]

    transactionType = models.PositiveSmallIntegerField(choices=TYPES)
    transactionReason = models.PositiveSmallIntegerField(choices=REASONS)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.IntegerField()  # Price in cents
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.PROTECT)
    stripe_charge_id = models.CharField(max_length=150, blank=True)
    errorMessage = models.CharField(max_length=150, blank=True)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def displayAmount(self):
        return (float(self.amount)) / 100

    @property
    def displayReason(self):
        return get_value(Transaction.REASONS, self.transactionReason)

    objects = TransactionManager()

    def __str__(self):
        return self.user.username + ' | ' + get_value(Transaction.TYPES, self.transactionType) \
               + ' ' + str(self.amount) + ' [' + self.displayReason + ']'
