from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user))
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
    # looking for gender, age range, purpose
    summary = models.TextField(max_length=2000, blank=True)
    contactInfo = models.CharField(max_length=150, blank=True)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fullName
