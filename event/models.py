import io
import logging
import re
from datetime import timedelta

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill

from account.models import Account
from money.models import Product

LOGGER = logging.getLogger(__name__)


# Return a value from a tuple list by key
def get_value(tuples, key):
    dictionary = dict(tuples)
    if key in dictionary:
        return dictionary[key]

    return ''


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
    def search(self, **kwargs):
        # Initial search by date
        hour_from_now = timezone.now() + timedelta(hours=1)
        filter_query = self.filter(startDateTime__gte=hour_from_now, hidden=False, deleted=False,
                                   stage__in=[Event.REGISTRATION_OPEN, Event.CONFIRMED])

        # Search by distance
        if 'cityLat' in kwargs and 'cityLng' in kwargs and 'distance' in kwargs and 'distanceUnits' in kwargs:
            lat = kwargs.get('cityLat')
            lng = kwargs.get('cityLng')
            distance = kwargs.get('distance')
            distance_units = kwargs.get('distanceUnits')
            # logger.info('distance: ' + str(distance))
            point = Point(x=lng, y=lat, srid=4326)
            radius = Distance(km=distance)
            if distance_units == 'mi':
                radius = Distance(mi=distance)
            filter_query = filter_query.filter(locationCoordinates__distance_lte=(point, radius))
            # logger.info('found ' + str(len(filter_query)))

        # Search text
        if 'search_term' in kwargs:
            search_term = kwargs.get('search_term')
            if search_term:
                # logger.info('term: ' + search_term)
                vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
                query = get_query(search_term)
                filter_query = filter_query.annotate(rank=SearchRank(vector, query)) \
                    .filter(rank__gte=0.1) \
                    .order_by('-rank')
                # logger.info('found ' + str(len(filter_query)))

        # Search by event types
        event_type_list = kwargs.get('eventTypeList').split('|') if kwargs.get('eventTypeList') else []
        if len(event_type_list):
            # logger.info('event_type_list: ' + str(event_type_list))
            filter_query = filter_query.filter(type__in=event_type_list)
            # logger.info('found ' + str(len(filter_query)))
        event_size_list = kwargs.get('eventSizeList').split('|') if kwargs.get('eventSizeList') else []
        if len(event_size_list):
            # logger.info('event_size_list: ' + str(event_size_list))
            filter_query = filter_query.filter(size__in=event_size_list)
            # logger.info('found ' + str(len(filter_query)))

        # ===========
        # Order query
        # ===========
        filter_query = filter_query.order_by('startDateTime')

        # ================
        # Advanced filters
        # ================
        result = []
        for event in filter_query:
            # Filter out full events
            if 'show_full' not in kwargs or kwargs.get('show_full') is False:
                if event.filledPercentage == 100:
                    continue

            # Advanced filtering by group genders
            sexual_identity = kwargs.get('sexual_identity')
            age = kwargs.get('age')
            user = {'sexualIdentity': sexual_identity, 'age': age}

            looking_for_gender_list = kwargs.get('lookingForGenderList').split('|') \
                if 'lookingForGenderList' in kwargs else []
            looking_for_age_min = kwargs.get('lookingForAgeMin') if 'lookingForAgeMin' in kwargs else 18
            looking_for_age_max = kwargs.get('lookingForAgeMax') if 'lookingForAgeMax' in kwargs else 120
            looking_for = []
            for sexual_identity in looking_for_gender_list:
                looking_for.append(
                    {'sexualIdentity': sexual_identity, 'ageMin': looking_for_age_min, 'ageMax': looking_for_age_max})
            if not event.groupsMatchCriteria(user, looking_for):
                continue

            result.append(event)

        return result

    # Filter events based on the distance from the given point
    def filter_by_distance(self, lng, lat, distance, distance_units='km'):
        point = Point(x=lng, y=lat, srid=4326)
        radius = Distance(km=distance)
        if distance_units == 'mi':
            radius = Distance(mi=distance)
        return self.filter(locationCoordinates__distance_lte=(point, radius))

    # Search events by text in name and description
    def search_text(self, text):
        vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
        query = get_query(text)
        # return self.annotate(rank=SearchRank(vector, query)).order_by('-rank', 'startDateTime')
        return self.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.1).order_by('-rank', 'startDateTime')

    # Get all future events that belong to the given user
    def get_all_future_by_user(self, user):
        return self.filter(eventgroup__eventparticipant__user=user).filter(
            startDateTime__gte=timezone.now()).order_by('startDateTime')

    # Get all past events that belong to the given user
    def get_all_past_by_user(self, user):
        return self.filter(eventgroup__eventparticipant__user=user).filter(
            startDateTime__lt=timezone.now()).order_by('-startDateTime')

    # Get all past events that belong to the given user
    def get_all_created_by_user(self, user):
        return self.filter(creator=user).order_by('-startDateTime')

    # Get next event that the user is registered for
    def get_next(self, user):
        now = timezone.now()
        event = self.get_all_future_by_user(user).filter(startDateTime__gte=now).order_by('-startDateTime').first()
        return event

    # Get the event that belongs to the user and is either starting in one hour,
    # is in progress now or ended up to half an hour ago
    def get_current(self, user):
        now = timezone.now()
        hour_from_now = now + timedelta(hours=1)
        half_hour_ago = now - timedelta(minutes=30)
        events = self.filter(eventgroup__eventparticipant__user=user).order_by('-startDateTime')

        for event in events:
            if event.startDateTime <= hour_from_now and event.endDateTime >= half_hour_ago:
                return event

        return None


class Event(models.Model):
    # Date is 5 minutes long by default
    DEFAULT_DATE_DURATION = 300
    # Date is 1 minute long by default
    DEFAULT_BREAK_DURATION = 60

    # Event sizes
    SMALL = 10
    MEDIUM = 20
    LARGE = 30

    # Event types
    SERIOUS = 1
    CASUAL = 2
    HOOKUP = 3
    FRIENDSHIP = 4
    MARRIAGE = 5

    # Event stages
    REGISTRATION_OPEN = 1
    CONFIRMED = 2
    IN_PROGRESS = 3
    CANCELLED = 4
    COMPLETED = 5

    SIZES = [
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large')
    ]

    # Number of groups
    NUM_GROUPS = [
        (1, 'One group (talk to everyone)'),
        (2, 'Two groups (talk to all members of the opposite group)')
    ]

    TYPES = [
        (MARRIAGE, 'Marriage'),
        (SERIOUS, 'Serious relationship'),
        (CASUAL, 'Casual dating'),
        (HOOKUP, 'Casual hookup'),
        (FRIENDSHIP, 'Friendship')
    ]

    STAGES = [
        (REGISTRATION_OPEN, 'Registration open'),
        (CONFIRMED, 'Confirmed'),
        (IN_PROGRESS, 'In progress'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed')
    ]

    # General info
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    type = models.PositiveSmallIntegerField(choices=TYPES, default=SERIOUS)
    stage = models.PositiveSmallIntegerField(choices=STAGES, default=REGISTRATION_OPEN)
    size = models.PositiveSmallIntegerField(choices=SIZES, default=MEDIUM)
    startDateTime = models.DateTimeField()
    locationName = models.CharField(max_length=150)
    locationCoordinates = gis_models.PointField(srid=4326, default=Point(0, 0))
    # Description
    description = models.TextField(max_length=2000, blank=True)
    # Group settings
    numGroups = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)],
                                                 choices=NUM_GROUPS, default=2)
    maxParticipantsInGroup = models.PositiveSmallIntegerField(validators=[MinValueValidator(5), MaxValueValidator(25)])
    # Date settings
    dateDuration = models.PositiveSmallIntegerField(validators=[MinValueValidator(60 * 3), MaxValueValidator(60 * 10)],
                                                    default=DEFAULT_DATE_DURATION)
    breakDuration = models.PositiveSmallIntegerField(validators=[MinValueValidator(60 / 2), MaxValueValidator(60 * 5)],
                                                     default=DEFAULT_BREAK_DURATION)
    # Image
    photo = models.ImageField(blank=True)
    photoMedium = ImageSpecField(source='photo',
                                 processors=[ResizeToFill(250, 250)],
                                 format='JPEG',
                                 options={'quality': 80})
    # Associated product
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    # Deleted flag
    deleted = models.BooleanField(default=False)
    # Hidden flag
    hidden = models.BooleanField(default=False)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Virtual fields
    # Calculate end time
    @cached_property
    def endDateTime(self):
        return self.startDateTime + timedelta(
            seconds=self.maxParticipantsInGroup * (self.dateDuration + self.breakDuration))

    @cached_property
    def duration(self):
        if self.numGroups == 1:
            return int((self.maxParticipantsInGroup - 1) * (self.dateDuration + self.breakDuration) / 60)
        elif self.numGroups == 2:
            return int(self.maxParticipantsInGroup * (self.dateDuration + self.breakDuration) / 60)

    @cached_property
    def numPeopleYouMeet(self):
        if self.numGroups == 1:
            return self.maxParticipantsInGroup - 1
        elif self.numGroups == 2:
            return self.maxParticipantsInGroup

    @cached_property
    def displayType(self):
        return get_value(Event.TYPES, self.type)

    @property
    def numberOfParticipants(self):
        participants = EventParticipant.objects.filter(group__in=self.eventgroup_set.all(),
                                                       status__in=[EventParticipant.REGISTERED,
                                                                   EventParticipant.PAYMENT_SUCCESS])
        return participants.count()

    @property
    def filledPercentage(self):
        num_participants = self.numberOfParticipants
        max_participants = self.numGroups * self.maxParticipantsInGroup
        return round(float(num_participants) / max_participants * 100)

    objects = EventManager()

    # Check if the event has groups that match the given criteria
    def groupsMatchCriteria(self, user, looking_for):
        groups = EventGroup.objects.filter(event=self.id)

        if self.numGroups == 1:
            if groups[0].user_matches(user) and groups[0].looking_for_matches(looking_for):
                return True
        elif self.numGroups == 2:
            if groups[0].user_matches(user) and groups[1].looking_for_matches(looking_for) or \
                    groups[1].user_matches(user) and groups[0].looking_for_matches(looking_for):
                return True

        return False

    # Return True if the user is registered in any group of this event
    def is_user_registered(self, user):
        try:
            EventParticipant.objects.get(user=user, group__in=self.eventgroup_set.all(),
                                         status__in=[EventParticipant.REGISTERED, EventParticipant.PAYMENT_SUCCESS])
            return True
        except EventParticipant.DoesNotExist:
            return False

    # Return True if the user is on the waiting list
    def is_user_on_waiting_list(self, user):
        try:
            EventParticipant.objects.get(user=user, group__in=self.eventgroup_set.all(),
                                         status=EventParticipant.WAITING_LIST)
            return True
        except EventParticipant.DoesNotExist:
            return False

    # Get number of hours until event start time
    def get_hours_until_start(self):
        num_seconds = self.get_seconds_until_start()
        return int(round(num_seconds / 3600, 0))

    # Get number of seconds until the event's start time
    def get_seconds_until_start(self):
        now = timezone.now()
        num_seconds = (self.startDateTime - now).total_seconds()
        return num_seconds

    # Get number of seconds since the event's start time
    def get_seconds_since_start(self):
        now = timezone.now()
        num_seconds = (now - self.startDateTime).total_seconds()
        return num_seconds

    # Return true if the event is happening right now
    def is_in_progress(self):
        seconds_since_start = self.get_seconds_since_start()
        duration_in_seconds = self.duration * 60
        return 0 < seconds_since_start < duration_in_seconds + 3600

    # Return true if the event is starting in the future (more than 1 hour from now)
    def is_in_future(self):
        seconds_until_start = self.get_seconds_until_start()
        return seconds_until_start >= 3600

    # Return true if the event is starting within one hour
    def is_starting_soon(self):
        seconds_until_start = self.get_seconds_until_start()
        return 0 < seconds_until_start < 3600

    # Return true if the event is starting within one hour
    def is_starting_within_a_day(self):
        seconds_until_start = self.get_seconds_until_start()
        return 0 < seconds_until_start < 3600 * 24

    # Return true if the event has ended at most half an hour ago
    def is_ended_recently(self):
        seconds_since_start = self.get_seconds_since_start()
        duration_in_seconds = self.duration * 60
        return duration_in_seconds < seconds_since_start < duration_in_seconds + 1800

    # Add a photo from a byte stream
    def add_photo(self, byte_stream, size=800, x=None, y=None, w=None, h=None):
        image = Image.open(byte_stream)

        if x and y and w and h:
            # Crop and resize the image
            cropped_image = image.crop((x, y, w + x, h + y))
            final_image = cropped_image.resize((size, size), Image.ANTIALIAS)
        else:
            final_image = image.resize((size, size), Image.ANTIALIAS)

        # Save the image
        stream = io.BytesIO()
        final_image.save(stream, 'JPEG')

        # Reopen the file for writing
        path = 'event-photos/event_' + str(self.pk) + '-' + get_random_string(length=6) + '.jpg'
        file = default_storage.open(path, 'wb')
        file.write(stream.getvalue())
        file.close()

        # Clean up old photo and thumbnails
        if self.photo is not None and self.photo.name != '':
            # Delete the old image file
            default_storage.delete(self.photo.name)
            logging.debug('Deleted file: ' + self.photo.name)

            cache_path = 'CACHE/images/' + self.photo.name.replace('.jpg', '') + '/'
            cached_files = default_storage.listdir(cache_path)
            for f in cached_files[1]:
                default_storage.delete(cache_path + f)
                logging.debug('Deleted file: ' + cache_path + f)

        self.photo = path
        self.save(update_fields=['photo'])

    # Add a photo by reading a file
    def add_photo_from_file(self, file, size, x, y, w, h):
        # Open the stream as an image
        stream = io.BytesIO(file)
        self.add_photo(stream, size, x, y, w, h)

    # To string
    def __str__(self):
        stage = get_value(Event.STAGES, self.stage)
        return str(self.id) + ' | ' + self.name + ' @ ' + self.locationName + ', ' + stage + \
            ' [' + str(self.startDateTime) + ']'


class EventGroup(models.Model):
    FEMALE = 'female'
    MALE = 'male'
    OTHER = 'other'
    ANY = 'any'

    IDENTITY_CHOICES = (
        (FEMALE, 'Women'),
        (MALE, 'Men'),
        (OTHER, 'Other (please specify)'),
        (ANY, 'Anyone welcome')
    )

    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    sexualIdentity = models.CharField(max_length=50, choices=IDENTITY_CHOICES, blank=True)
    sexualIdentityOther = models.CharField(max_length=150, blank=True)
    ageMin = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)])
    ageMax = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)])

    @cached_property
    def displaySexualIdentity(self):
        if self.sexualIdentity == 'other':
            return self.sexualIdentityOther
        else:
            return get_value(EventGroup.IDENTITY_CHOICES, self.sexualIdentity)

    # Check if user's sexual identity and age matches the group
    def user_matches(self, user):
        if self.ageMin <= user.get('age') <= self.ageMax:
            if self.sexualIdentity == EventGroup.ANY \
                    or self.sexualIdentity == EventGroup.OTHER \
                    or self.sexualIdentity == user.get('sexualIdentity'):
                return True

        return False

    # Check if any object in looking_for array matches the group
    def looking_for_matches(self, looking_for_array):
        for looking_for in looking_for_array:
            if self.ageMin <= looking_for.get('ageMax') and looking_for.get('ageMin') <= self.ageMax:
                if self.sexualIdentity == EventGroup.ANY \
                        or self.sexualIdentity == EventGroup.OTHER \
                        or self.sexualIdentity == looking_for.get('sexualIdentity') \
                        or looking_for.get('sexualIdentity') is None \
                        or looking_for.get('sexualIdentity') == '':
                    return True

        return False

    # Check if the user is able to register and raise an appropriate exception if not
    def can_user_register(self, user):
        # Check if the event is in the future
        if not self.event.is_in_future:
            raise Exception(_('Registration is closed'))

        # Check if the group has spots
        num_participants = self.count_registered_participants()
        if self.event.maxParticipantsInGroup <= num_participants:
            raise Exception(_('Group is full'))

        # Check that the user is not already registered
        if self.event.is_user_registered(user):
            raise Exception(_('You are already registered'))

        # Check that sexual identity matches (male or female only)
        account = Account.objects.get(user=user)
        if self.sexualIdentity == EventGroup.MALE or self.sexualIdentity == EventGroup.FEMALE:
            if self.sexualIdentity != account.sexualIdentity:
                raise Exception(_('This group does not match your sexual identity'))

        # Check that the age range includes user's age
        if self.ageMin > account.age or self.ageMax < account.age:
            raise Exception(_('This group does not match your age'))

        return True

    def get_registered_participants(self):
        participants = EventParticipant.objects.filter(group=self, status=EventParticipant.REGISTERED) \
            .order_by('created')
        return participants

    def get_registered_participants_accounts(self):
        users = []
        for participant in self.get_registered_participants():
            users.append(participant.user)
        return Account.objects.filter(user__in=users)

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
        # Check if user can register
        self.can_user_register(user)

        # Check if the user is on the waiting list
        if self.event.is_user_on_waiting_list(user):
            raise Exception(_('You are already on a waiting list'))
        else:
            participant = EventParticipant(group=self, user=user, status=EventParticipant.REGISTERED)
            participant.save()

        # Check if the event is starting within 24 hours and process payment
        if self.event.is_starting_within_a_day():
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
        return str(self.event) + ' | ' + self.sexualIdentity + ' [' + str(self.ageMin) + ' - ' + str(self.ageMax) + ']'


class EventParticipant(models.Model):
    # Statuses
    REGISTERED = 'registered'
    WAITING_LIST = 'waiting_list'
    PAYMENT_SUCCESS = 'payment_success'
    PAYMENT_FAILURE = 'payment_failure'

    group = models.ForeignKey(EventGroup, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    STATUSES = (
        (REGISTERED, 'registered'),
        (WAITING_LIST, 'waiting_list'),
        (PAYMENT_SUCCESS, 'payment_success'),
        (PAYMENT_FAILURE, 'payment_failure'),
    )
    status = models.CharField(max_length=20, choices=STATUSES)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + ' [' + str(self.user.id) + '] ' + ' in event: ' + self.group.event.name


class PickManager(models.Manager):
    def get_all_matches_by_user(self, user):
        events = Event.objects.get_all_past_by_user(user)
        result = {}
        for event in reversed(events):
            matches = self.get_all_matches_by_user_and_event(user, event)
            if len(matches) > 0:
                result[event] = matches

        return result

    def get_all_matches_by_user_and_event(self, user, event):
        all_matches = []
        # Get all picks from an event
        for users_pick in self.filter(picker=user, event=event, response=Pick.YES):
            if len(self.filter(picker=users_pick.picked, picked=user, event=event, response=Pick.YES)) > 0:
                all_matches.append(users_pick.picked)
        return all_matches

    def get_response(self, user, picked, event):
        try:
            p = self.get(picker=user, picked=picked, event=event)
        except Pick.DoesNotExist:
            p = Pick(picker=user, picked=picked, event=event, response=2)
            p.save()

        return p.response

    def pick(self, user, picked, event, response):
        # Check if the pick exists
        try:
            p = self.get(picker=user, picked=picked, event=event)
            # Update response
            p.response = response
        except Pick.DoesNotExist:
            p = Pick(picker=user, picked=picked, event=event, response=response)

        p.save()
        return p

    def pick_by_id(self, user, picked_id, event_id, response):
        picked = get_user_model().objects.get(id=picked_id)

        event = Event.objects.get(id=event_id)

        return self.pick(user, picked, event, response)

    def is_familiar(self, user, picked):
        # Check if the pick exists in one direction
        if self.filter(picker=user, picked=picked).count() > 0:
            return True

        return False

    def is_match(self, user, picked):
        # Check if the pick exists in both directions
        for users_pick in self.filter(picker=user, picked=picked, response=Pick.YES):
            try:
                self.get(picker=picked, picked=user, event=users_pick.event, response=Pick.YES)
                return True
            except Pick.DoesNotExist:
                continue

        return False


class Pick(models.Model):
    # Choice
    YES = 1
    NO = 0
    MAYBE = 2

    picker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='picked_by', on_delete=models.PROTECT)
    picked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='picked', on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    RESPONSES = (
        (YES, 'liked'),
        (NO, 'did not like'),
        (MAYBE, 'maybe liked')
    )
    response = models.PositiveSmallIntegerField(default=MAYBE, choices=RESPONSES)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = PickManager()

    def __str__(self):
        if self.response == self.YES:
            return 'User ' + str(self.picker) + ' LIKED ' + str(self.picked) + ' at event ' + str(self.event)

        if self.response == self.NO:
            return 'User ' + str(self.picker) + ' DID NOT LIKE ' + str(self.picked) + ' at event ' + str(self.event)

        if self.response == self.MAYBE:
            return 'User ' + str(self.picker) + ' MAYBE LIKED ' + str(self.picked) + ' at event ' + str(self.event)
