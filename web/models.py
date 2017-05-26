import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from money.models import Product


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class Event(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user)
    )
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    description = models.TextField(max_length=2000, blank=True)
    maxParticipantsInGroup = models.PositiveSmallIntegerField(validators=[MinValueValidator(5), MaxValueValidator(25)])
    startDateTime = models.DateTimeField()
    product = models.ForeignKey(Product)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + ' @ ' + self.location + ', [' + str(self.startDateTime) + ']'

    def is_registered(self, user):
        try:
            EventParticipant.objects.get(user=user, group__in=self.eventgroup_set.all(),
                                         status__in=[EventParticipant.REGISTERED, EventParticipant.PAYMENT_SUCCESS])
            return True
        except EventParticipant.DoesNotExist:
            return False

    def is_on_waiting_list(self, user):
        try:
            EventParticipant.objects.get(user=user, group__in=self.eventgroup_set.all(),
                                         status=EventParticipant.WAITING_LIST)
            return True
        except EventParticipant.DoesNotExist:
            return False


class EventGroup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    ageMin = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)])
    ageMax = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)])

    def get_registered_participants(self):
        participants = EventParticipant.objects.filter(group=self, status=EventParticipant.REGISTERED) \
            .order_by('created')
        return participants

    def count_registered_participants(self):
        participants = EventParticipant.objects.filter(group=self, status=EventParticipant.REGISTERED)
        return participants.count()

    def get_waiting_list_participants(self):
        participants = EventParticipant.objects.filter(group=self, status=EventParticipant.WAITING_LIST) \
            .order_by('created')
        return participants

    def count_waiting_list_participants(self):
        participants = EventParticipant.objects.filter(group=self, status=EventParticipant.WAITING_LIST)
        return participants.count()

    def add_participant(self, user):
        # Check if the event is in the past
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.event.startDateTime < now:
            # TODO: process payment right away
            raise Exception(_('The event is in the past'))

        # Check if the group is full
        num_participants = self.count_registered_participants()
        if self.event.maxParticipantsInGroup <= num_participants:
            raise Exception(_('Group is full'))

        # Check if the user is already registered
        if self.event.is_registered(user):
            raise Exception(_('You are already registered'))

        # Check if the user is on the waiting list
        if self.event.is_on_waiting_list(user):
            raise Exception(_('You are already on a waiting list'))
        else:
            participant = EventParticipant(group=self, user=user, status=EventParticipant.REGISTERED)
            participant.save()

        # Check if the event is starting within 24 hours and process payment
        time_diff = self.event.startDateTime - now
        if time_diff.days < 1:
            # TODO: process payment right away
            raise Exception(_('Pay first'))

    def add_participant_to_waiting_list(self, user):
        return None

    def remove_participant(self, user):
        return None

    def remove_participant_from_waiting_list(self, user):
        return None

    def register_participant_from_waiting_list(self, user):
        return None

    def __str__(self):
        return self.name + ' [' + str(self.ageMin) + ' - ' + str(self.ageMax) + ']'


class EventParticipant(models.Model):
    # Statuses
    REGISTERED = 'registered'
    WAITING_LIST = 'waiting_list'
    PAYMENT_SUCCESS = 'payment_success'
    PAYMENT_FAILURE = 'payment_failure'

    group = models.ForeignKey(EventGroup, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    STATUSES = (
        ('registered', REGISTERED),
        ('waiting_list', WAITING_LIST),
        ('payment_success', PAYMENT_SUCCESS),
        ('payment_failure', PAYMENT_FAILURE),
    )
    status = models.CharField(max_length=20, choices=STATUSES)

    # Automatic timestamp
    created = models.DateTimeField(auto_now_add=True)


class PickManager(models.Manager):
    def get_query_set(self):
        return models.QuerySet(self.model, using=self._db)

    def get_matches(self, user, event):
        matches = []
        # Get all picks from an event
        for users_pick in self.get_query_set().filter(picker=user, event=event):
            if len(self.get_query_set().filter(picker=users_pick.picked, picked=user, event=event)) > 0:
                matches.append(users_pick.picked)
        return matches


class Pick(models.Model):
    picker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='picked_by')
    picked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='picked')
    event = models.ForeignKey(Event)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)

    # def pick(self, picker, picked, event):
    #     p = Pick(picker=picker, picked=picked, event=event)
    #     return p

    # Custom manager
    objects = PickManager()

    def __str__(self):
        return 'User ' + str(self.picker) + ' picked ' + str(self.picked) + ' at event ' + str(self.event)
