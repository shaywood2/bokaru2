from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import Event, EventGroup


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ['creator']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        else:
            raise Exception('No user provided')

        super(EventForm, self).__init__(*args, **kwargs)

    # isSingleGroup = forms.BooleanField()

    # First group data
    # group1Name = forms.CharField(max_length=150)
    # group1AgeMin = forms.IntegerField(min_value=18)
    # group1AgeMax = forms.IntegerField(min_value=18)
    # group1ParticipantsMaxNumber = forms.IntegerField(min_value=5, max_value=20)
    #
    # # Second group data
    # group2Name = forms.CharField(max_length=150, required=False)
    # group2AgeMin = forms.IntegerField(min_value=18, required=False)
    # group2AgeMax = forms.IntegerField(min_value=18, required=False)
    # group2ParticipantsMaxNumber = forms.IntegerField(min_value=5, max_value=20, required=False)

    def save(self, commit=True):
        # Set creator to the current user
        event = super(EventForm, self).save(commit=False)
        event.creator = self.user

        if commit:
            event.save()
        return event


class EventGroupForm(ModelForm):
    class Meta:
        model = EventGroup
        exclude = ['event', 'participants']

    def __init__(self, *args, **kwargs):
        if 'event' in kwargs:
            self.event = kwargs.pop('event')
        else:
            raise Exception('No event provided')

        super(EventGroupForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        # Set creator to the current user
        event_group = super(EventGroupForm, self).save(commit=False)
        event_group.event = self.event

        if commit:
            event_group.save()
        return event_group
