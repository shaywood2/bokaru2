from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


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
    startDateTime = models.DateTimeField()

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + ' @ ' + self.location + ', [' + str(self.startDateTime) + ']'


class EventGroup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    ageMin = models.PositiveSmallIntegerField()
    ageMax = models.PositiveSmallIntegerField()
    participantsMaxNumber = models.PositiveSmallIntegerField()
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.name + ' [' + str(self.ageMin) + ' - ' + str(self.ageMax) + ']'
