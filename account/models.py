from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from web.models import Event


def user_photo_file_name(instance, filename):
    return 'user-photos/' + instance.user.username + '.' + filename.split('.')[-1]


class Account(models.Model):
    STATUSES = (
        ('created', 'Created'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('deleted', 'Deleted')
    )
    ORIENTATIONS = (
        ('straight', 'Straight'),
        ('gay', 'Gay'),
        ('bisexual', 'Bisexual'),
        ('other', 'Other')
    )
    IDENTITIES = (
        ('woman', 'Woman'),
        ('man', 'Man'),
        ('other', 'Other')
    )
    RELATIONSHIP_STATUSES = (
        ('single', 'Single'),
        ('seeing_someone', 'Seeing someone'),
        ('married', 'Married'),
        ('open_relationship', 'Open relationship')
    )
    RELATIONSHIP_TYPES = (
        ('monogamous', 'Monogamous'),
        ('non_monogamous', 'Non-monogamous'),
    )
    BODY_TYPES = (
        ('thin', 'Thin'),
        ('fit', 'Fit'),
        ('average_build', 'Average build'),
        ('a_little_extra', 'A little extra'),
        ('curvy', 'Curvy'),
        ('overweight', 'Overweight')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    photo = models.ImageField(upload_to=user_photo_file_name)
    photo_thumbnail_large = ImageSpecField(source='photo',
                                           processors=[ResizeToFill(200, 200)],
                                           format='JPEG',
                                           options={'quality': 80})
    photo_thumbnail_small = ImageSpecField(source='photo',
                                           processors=[ResizeToFill(200, 200)],
                                           format='JPEG',
                                           options={'quality': 80})
    birthDate = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUSES, blank=True)
    gender = models.CharField(max_length=30, blank=True)
    fullName = models.CharField(max_length=150, blank=True)
    sexualOrientation = models.CharField(max_length=150, choices=ORIENTATIONS, blank=True)
    sexualIdentity = models.CharField(max_length=150, choices=IDENTITIES, blank=True)
    relationshipStatus = models.CharField(max_length=150, choices=RELATIONSHIP_STATUSES, blank=True)
    relationshipType = models.CharField(max_length=150, choices=RELATIONSHIP_TYPES, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bodyType = models.CharField(max_length=50, choices=BODY_TYPES, blank=True)
    ethnicity = models.CharField(max_length=150, blank=True)
    languages = models.CharField(max_length=150, blank=True)
    education = models.CharField(max_length=150, blank=True)
    religion = models.CharField(max_length=150, blank=True)
    vices = models.CharField(max_length=150, blank=True)
    kids = models.CharField(max_length=150, blank=True)
    diet = models.CharField(max_length=150, blank=True)
    summary = models.TextField(max_length=2000, blank=True)
    contactInfo = models.CharField(max_length=150, blank=True)
    locationName = models.CharField(max_length=150, blank=True)
    locationCoordinates = gis_models.PointField(srid=4326, default=Point(0, 0))

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def generate_image_cache(self):
        # Invalidate all ImageKit spec caches
        self.photo_thumbnail_large.generate()
        self.photo_thumbnail_small.generate()

    def __str__(self):
        return self.fullName


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

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # Event preferences
    ageMin = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)], blank=True)
    ageMax = models.PositiveSmallIntegerField(validators=[MinValueValidator(18)], blank=True)
    numGroups = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)],
                                                 choices=Event.NUM_GROUPS, blank=True)
    eventType = models.PositiveSmallIntegerField(choices=Event.TYPES, blank=True)
    eventSize = models.PositiveSmallIntegerField(choices=EVENT_SIZES, blank=True)

    # Communication preferences
    receiveNewsletter = models.BooleanField(default=True)

    # Misc preferences
    units = models.CharField(max_length=3, choices=UNITS, blank=True)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)
