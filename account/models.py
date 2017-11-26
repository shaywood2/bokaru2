import io
import logging

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

logger = logging.getLogger(__name__)


# Return a value from a tuple list by key
def get_value(tuples, key):
    dictionary = dict(tuples)
    if key in dictionary:
        return dictionary[key]

    return ''


class Account(models.Model):
    # Newly created account
    CREATED = 'created'
    # Completed account (can join events)
    COMPLETED = 'completed'
    # Suspended account (for infractions)
    SUSPENDED = 'suspended'
    # Deleted account (deleted by user)
    DELETED = 'deleted'

    STATUS = (
        (CREATED, 'Created'),
        (COMPLETED, 'Completed'),
        (SUSPENDED, 'Suspended'),
        (DELETED, 'Deleted')
    )
    ORIENTATION = (
        ('straight', 'Straight'),
        ('gay', 'Gay'),
        ('bisexual', 'Bisexual'),
        ('other', 'Other')
    )
    IDENTITY = (
        ('female', 'Woman'),
        ('male', 'Man'),
        ('other', 'Other')
    )
    RELATIONSHIP_STATUS = (
        ('single', 'Single'),
        ('seeing_someone', 'Seeing someone'),
        ('married', 'Married'),
        ('open_relationship', 'Open relationship')
    )
    RELATIONSHIP_TYPE = (
        ('monogamous', 'Monogamous'),
        ('non_monogamous', 'Non-monogamous'),
    )
    BODY_TYPE = (
        ('thin', 'Thin'),
        ('fit', 'Fit'),
        ('average_build', 'Average build'),
        ('a_little_extra', 'A little extra'),
        ('curvy', 'Curvy'),
        ('overweight', 'Overweight'),
        ('jacked', 'Jacked')
    )
    EDUCATION = (
        ('high_school', 'High school'),
        ('two_year_college', 'Two-year college'),
        ('university', 'University'),
        ('post_grad', 'Post grad'),
    )
    RELIGION = (
        ('agnostic', 'Agnostic'),
        ('atheist', 'Atheist'),
        ('christianity', 'Christian'),
        ('jewish', 'Jewish'),
        ('catholic', 'Catholic'),
        ('muslim', 'Muslim'),
        ('hindu', 'Hindu'),
        ('buddhist', 'Buddhist'),
        ('sikh', 'Sikh'),
        ('other', 'Other')
    )
    VICE_CHOICES = (
        ('often', 'Often'),
        ('sometimes', 'Sometimes'),
        ('never', 'Never')
    )
    KIDS_HAVE_CHOICES = (
        ('has', 'Has kid(s)'),
        ('doesnt_have', 'Doesn\'t have kids')
    )
    KIDS_WANT_CHOICES = (
        ('might_want', 'but might want them'),
        ('wants', 'but wants them'),
        ('doesnt_want', 'and doesn\'t want them'),
        ('might_want2', 'and might want more'),
        ('wants2', 'and wants more'),
        ('doesnt_want2', 'and doesn\'t want more')
    )
    DIET = (
        ('omnivore', 'Omnivore'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('kosher', 'Kosher'),
        ('halal', 'Halal')
    )
    # User model
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # Account status
    status = models.CharField(max_length=20, choices=STATUS, default=CREATED)
    # Photo
    photo = models.ImageField(blank=True)
    photoThumbnail = ImageSpecField(source='photo',
                                    processors=[ResizeToFill(30, 30)],
                                    format='JPEG',
                                    options={'quality': 60})
    # Location
    locationName = models.CharField(max_length=150, blank=True)
    locationCoordinates = gis_models.PointField(srid=4326, default=Point(0, 0))
    # Basic info
    birthDate = models.DateField(blank=True, null=True)
    fullName = models.CharField(max_length=150, blank=True)
    sexualOrientation = models.CharField(max_length=50, choices=ORIENTATION, blank=True)
    sexualOrientationOther = models.CharField(max_length=150, blank=True)
    sexualIdentity = models.CharField(max_length=50, choices=IDENTITY, blank=True)
    sexualIdentityOther = models.CharField(max_length=150, blank=True)
    relationshipStatus = models.CharField(max_length=50, choices=RELATIONSHIP_STATUS, blank=True)
    relationshipType = models.CharField(max_length=50, choices=RELATIONSHIP_TYPE, blank=True)
    height = models.PositiveSmallIntegerField(blank=True, null=True)
    bodyType = models.CharField(max_length=50, choices=BODY_TYPE, blank=True)
    # Background
    # TODO: calculate max possible size
    ethnicityList = models.CharField(max_length=500, blank=True)
    # TODO: calculate max possible size
    languageList = models.CharField(max_length=500, blank=True)
    education = models.CharField(max_length=50, choices=EDUCATION, blank=True)
    religion = models.CharField(max_length=50, choices=RELIGION, blank=True)
    # Details
    viceSmoking = models.CharField(max_length=50, choices=VICE_CHOICES, blank=True)
    viceDrinking = models.CharField(max_length=50, choices=VICE_CHOICES, blank=True)
    viceDrugs = models.CharField(max_length=50, choices=VICE_CHOICES, blank=True)
    kidsHave = models.CharField(max_length=50, choices=KIDS_HAVE_CHOICES, blank=True)
    kidsWant = models.CharField(max_length=50, choices=KIDS_WANT_CHOICES, blank=True)
    # TODO: calculate max possible size
    petList = models.CharField(max_length=500, blank=True)
    diet = models.CharField(max_length=50, choices=DIET, blank=True)
    # Summary
    summary = models.TextField(max_length=2000, blank=True)
    # Contact info
    contactInfo = models.CharField(max_length=150, blank=True)
    # Looking for
    # TODO: calculate max possible size
    lookingForGenderList = models.CharField(max_length=500, blank=True)
    lookingForAgeMin = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)], blank=True, null=True)
    lookingForAgeMax = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)], blank=True, null=True)
    # TODO: calculate max possible size
    lookingForConnectionsList = models.CharField(max_length=500, blank=True)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Virtual fields
    @property
    def age(self):
        if self.birthDate is None:
            return None

        today = timezone.now()
        years_difference = today.year - self.birthDate.year
        is_before_birthday = (today.month, today.day) < (self.birthDate.month, self.birthDate.day)
        elapsed_years = years_difference - int(is_before_birthday)
        return elapsed_years

    @property
    def basicInfo(self):
        result = []

        if self.sexualOrientation != '':
            if self.sexualOrientation == 'other':
                result.append('Other orientation: ' + str(self.sexualOrientationOther))
            else:
                result.append(get_value(self.ORIENTATION, self.sexualOrientation))

        if self.sexualIdentity != '':
            if self.sexualIdentity == 'other':
                result.append('Other gender: ' + str(self.sexualIdentityOther))
            else:
                result.append(get_value(self.IDENTITY, self.sexualIdentity))

        if self.relationshipStatus != '':
            result.append(get_value(self.RELATIONSHIP_STATUS, self.relationshipStatus))

        if self.relationshipType != '':
            result.append(get_value(self.RELATIONSHIP_TYPE, self.relationshipType))

        if self.height is not None:
            # TODO: convert into preferred units
            result.append(str(round(int(self.height), 0)) + 'cm')

        if self.bodyType != '':
            result.append(get_value(self.BODY_TYPE, self.bodyType))

        return result

    @property
    def background(self):
        result = []
        if self.ethnicityList != '':
            result.append(', '.join(self.ethnicityList.split('|')))

        if self.languageList != '':
            result.append('Speaks ' + ', '.join(self.languageList.split('|')))

        if self.education != '':
            result.append('Attended ' + get_value(self.EDUCATION, self.education))

        if self.religion != '':
            result.append(get_value(self.RELIGION, self.religion))

        return result

    @property
    def details(self):
        result = []

        if self.viceSmoking != '':
            result.append('Smokes: ' + get_value(self.VICE_CHOICES, self.viceSmoking))

        if self.viceDrinking != '':
            result.append('Drinks: ' + get_value(self.VICE_CHOICES, self.viceDrinking))

        if self.viceDrugs != '':
            result.append('Does drugs: ' + get_value(self.VICE_CHOICES, self.viceDrugs))

        if self.diet != '':
            result.append(get_value(self.DIET, self.diet))

        if self.kidsHave != '':
            kids = get_value(self.KIDS_HAVE_CHOICES, self.kidsHave)

            if self.kidsWant != '':
                kids += ' ' + get_value(self.KIDS_WANT_CHOICES, self.kidsWant)

            result.append(kids)

        if self.petList != '':
            result.append('Pets: ' + ', '.join(self.petList.split('|')))

        return result

    @property
    def lookingFor(self):
        result = []

        if self.lookingForGenderList != '':
            result.append(', '.join(self.lookingForGenderList.split('|')))

        if self.lookingForAgeMin and self.lookingForAgeMax:
            result.append('ages ' + str(self.lookingForAgeMin) + '-' + str(self.lookingForAgeMax))

        if self.lookingForConnectionsList != '':
            result.append(', '.join(self.lookingForConnectionsList.split('|')))

        return result

    def can_join_events(self):
        if self.status == Account.COMPLETED:
            return True
        return False

    def add_photo(self, new_photo, x, y, w, h, size):
        # Open the stream as an image
        stream = io.BytesIO(new_photo)
        image = Image.open(stream)

        # Crop and resize the image
        cropped_image = image.crop((x, y, w + x, h + y))
        final_image = cropped_image.resize((size, size), Image.ANTIALIAS)

        # Save the image
        stream = io.BytesIO()
        final_image.save(stream, 'JPEG')

        # Reopen the file for writing
        path = 'user-photos/' + self.user.username + '-' + get_random_string(length=6) + '.jpg'
        file = default_storage.open(path, 'wb')
        file.write(stream.getvalue())
        file.close()

        # Clean up old photo and thumbnails
        if self.photo is not None and self.photo.name != '':
            # Delete the old image file
            default_storage.delete(self.photo.name)
            logging.debug('Deleted file: ' + self.photo.name)

            cache_path = 'CACHE/images/' + self.photo.name.replace('.jpg', '') + '/'
            try:
                cached_files = default_storage.listdir(cache_path)
                for f in cached_files[1]:
                    default_storage.delete(cache_path + f)
                    logging.debug('Deleted file: ' + cache_path + f)
            except FileNotFoundError as err:
                logging.error('file not found ' + str(err))

        self.photo = path
        self.save(update_fields=['photo'])

    def __str__(self):
        return self.user.username + ' (' + self.fullName + ')'


class UserPreference(models.Model):
    EVENT_SIZES = (
        (10, 'Small'),
        (20, 'Medium'),
        (30, 'Large')
    )
    UNITS = (
        ('km', 'Kilometers'),
        ('m', 'Miles')
    )
    NUM_GROUPS = [
        (1, 'One group (talk to everyone)'),
        (2, 'Two groups (talk to all members of the opposite group)')
    ]
    SERIOUS = 1
    CASUAL = 2
    HOOKUP = 3
    FRIENDSHIP = 4
    MARRIAGE = 5
    TYPES = [
        (MARRIAGE, 'Marriage'),
        (SERIOUS, 'Serious relationship'),
        (CASUAL, 'Casual dating'),
        (HOOKUP, 'Casual hookup'),
        (FRIENDSHIP, 'Friendship')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # Event preferences
    ageMin = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)], default=18)
    ageMax = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)], default=99)
    numGroups = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)],
                                                 choices=NUM_GROUPS, blank=True, null=True)
    eventType = models.PositiveSmallIntegerField(choices=TYPES, blank=True, null=True)
    eventSize = models.PositiveSmallIntegerField(choices=EVENT_SIZES, blank=True, null=True)

    # Communication preferences
    receiveNewsletter = models.BooleanField(default=False)

    # Misc preferences
    units = models.CharField(max_length=3, choices=UNITS, default='km')

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class MemoManager(models.Manager):
    def create_or_update_memo(self, owner, about, content):
        # Check if the memo exists
        try:
            m = self.get(owner=owner, about=about)
            # Update content
            m.content = content
        except Memo.DoesNotExist:
            m = Memo(owner=owner, about=about, content=content)

        m.save()
        return m

    def create_or_update_memo_by_id(self, owner, about_id, content):
        about = get_user_model().objects.get(id=about_id)

        return self.create_or_update_memo(owner, about, content)

    def get_memo_content(self, owner, about):
        try:
            m = self.get(owner=owner, about=about)
            return str(m.content)
        except Memo.DoesNotExist:
            return ''


class Memo(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner')
    about = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='about')
    content = models.TextField(max_length=2000, blank=True)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = MemoManager()

    def __str__(self):
        return str(self.owner) + ' (' + str(self.about) + '): ' + self.content
