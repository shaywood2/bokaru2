import datetime
import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from money.models import Product


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


# Splits the query string in individual keywords, getting rid of unnecessary spaces and grouping quoted words together.
def normalize_query(query_string,
                    find_terms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    norm_space=re.compile(r'\s{2,}').sub):
    return [norm_space(' ', (t[0] or t[1]).strip()) for t in find_terms(query_string)]


# Construct a query based on an input string, basically OR all individual words
def get_query(query_string):
    query = None
    terms = normalize_query(query_string)
    for term in terms:
        q = SearchQuery(term)
        if query is None:
            query = q
        else:
            query = query | q
    return query


class EventManager(models.Manager):
    # Filter events based on the distance from the given point
    def filter_by_distance(self, lat, lon, distance):
        point = Point(x=lat, y=lon, srid=4326)
        return self.filter(locationCoordinates__distance_lte=(point, D(km=distance)))

    # Search events by text in name and description
    def search_text(self, text):
        vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
        query = get_query(text)
        return self.annotate(rank=SearchRank(vector, query)).order_by('-rank', 'startDateTime')
        # return self.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.1).order_by('-rank', 'startDateTime')

    # Get all events that belong to the given user
    def get_all_by_user(self, user):
        return self.filter(eventgroup__eventparticipant__user=user).order_by('startDateTime')

    # Get next event that the user is registered for
    def get_next(self, user):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        event = self.get_all_by_user(user).filter(startDateTime__gte=now).order_by('-startDateTime').first()
        return event

    # Get the event that belongs to the user and is either starting in one hour, running now or ended up to one hour ago
    def get_current(self, user):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        hour_from_now = now + timedelta(hours=1)
        hour_ago = now - timedelta(hours=1)
        events = self.get_all_by_user(user).order_by('-startDateTime')

        for event in events:
            if event.startDateTime <= hour_from_now and event.endDateTime >= hour_ago:
                return event

        return None


class Event(models.Model):
    # The event must be at least 70% full to be confirmed
    CONFIRMED_MIN_PARTICIPANTS = 0.7

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user)
    )
    name = models.CharField(max_length=150)
    locationName = models.CharField(max_length=150)
    locationCoordinates = gis_models.PointField(srid=4326, default=Point(0, 0))
    description = models.TextField(max_length=2000, blank=True)
    numGroups = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)], default=2)
    maxParticipantsInGroup = models.PositiveSmallIntegerField(validators=[MinValueValidator(5), MaxValueValidator(25)])
    startDateTime = models.DateTimeField()
    dateDuration = models.PositiveSmallIntegerField(validators=[MinValueValidator(60 * 3), MaxValueValidator(60 * 10)],
                                                    default=60 * 5)
    breakDuration = models.PositiveSmallIntegerField(validators=[MinValueValidator(60 / 2), MaxValueValidator(60 * 5)],
                                                     default=60)
    product = models.ForeignKey(Product)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Virtual field
    @property
    def endDateTime(self):
        return self.startDateTime + timedelta(
            seconds=self.maxParticipantsInGroup * (self.dateDuration + self.breakDuration))

    objects = EventManager()

    def __str__(self):
        return self.name + ' @ ' + self.locationName + ', [' + str(self.startDateTime) + ']'

    def __lt__(self, other):
        return self.startDateTime < other.startDateTime

    def __hash__(self):
        return hash((self.name, self.locationName, self.startDateTime, self.id))

    #def __eq__(self, other):
    #    return self.id == other.id

    def __ne__(self, other):
        return not (self == other)

    # Return True if the user is registered in any group of this event
    def is_registered(self, user):
        try:
            EventParticipant.objects.get(user=user, group__in=self.eventgroup_set.all(),
                                         status__in=[EventParticipant.REGISTERED, EventParticipant.PAYMENT_SUCCESS])
            return True
        except EventParticipant.DoesNotExist:
            return False

    # Return True if the user is on the waiting list
    def is_on_waiting_list(self, user):
        try:
            EventParticipant.objects.get(user=user, group__in=self.eventgroup_set.all(),
                                         status=EventParticipant.WAITING_LIST)
            return True
        except EventParticipant.DoesNotExist:
            return False

    # Return True if the event is going to be held
    def is_confirmed(self):
        # The event must start within a day
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        time_diff = self.event.startDateTime - now
        if time_diff.days < 1:
            # Check if there are enough participants
            participants = EventParticipant.objects.filter(group__in=self.eventgroup_set.all(),
                                                           status__in=[EventParticipant.REGISTERED,
                                                                       EventParticipant.PAYMENT_SUCCESS])
            num_participants = participants.count()
            if num_participants / (self.maxParticipantsInGroup * self.numGroups) >= self.CONFIRMED_MIN_PARTICIPANTS:
                return True

        return False

    # Return true if the event is happening right now
    def is_in_progress(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        return self.startDateTime <= now <= self.endDateTime

    # Return true if the event is starting within one hour
    def is_starting_soon(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        hour_from_now = now + timedelta(hours=1)
        return now <= self.startDateTime <= hour_from_now

    # Return true if the event has ended at most one hour ago
    def is_ended_recently(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        hour_ago = now - timedelta(hours=1)
        return now >= self.endDateTime >= hour_ago


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
        raise Exception('Function not implemented: add_participant_to_waiting_list')

    def remove_participant(self, user):
        raise Exception('Function not implemented: remove_participant')

    def remove_participant_from_waiting_list(self, user):
        raise Exception('Function not implemented: remove_participant_from_waiting_list')

    def register_participant_from_waiting_list(self, user):
        raise Exception('Function not implemented: register_participant_from_waiting_list')

    def __str__(self):
        return self.name + ' [' + str(self.ageMin) + ' - ' + str(self.ageMax) + '] in event: ' + self.event.name


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

    def __str__(self):
        return self.user.username + ' [' + str(self.user.id) + '] ' + ' in event: ' + self.group.event.name


class PickManager(models.Manager):
    def get_all_matches_by_user(self, user):
        result = {}
        # Get all picks from an event
        for users_pick in self.filter(picker=user):
            if len(self.filter(picker=users_pick.picked, picked=user)) > 0:
                if users_pick.event not in result:
                    result[users_pick.event] = []

                result[users_pick.event].append(users_pick.picked)

        return result

    def get_all_matches_by_user_and_event(self, user, event):
        all_matches = []
        # Get all picks from an event
        for users_pick in self.filter(picker=user, event=event):
            if len(self.filter(picker=users_pick.picked, picked=user, event=event)) > 0:
                all_matches.append(users_pick.picked)
        return all_matches

    @staticmethod
    def pick(user, picked, event):
        p = Pick(picker=user, picked=picked, event=event)
        p.save()
        return p


class Pick(models.Model):
    # TODO: save "no" choices as well
    picker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='picked_by')
    picked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='picked')
    event = models.ForeignKey(Event)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)

    # Custom manager
    objects = PickManager()

    def __str__(self):
        return 'User ' + str(self.picker) + ' picked ' + str(self.picked) + ' at event ' + str(self.event)
