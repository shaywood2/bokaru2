from django.forms import ModelForm

from .models import Event, EventGroup


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ['creator']


class EventGroupForm(ModelForm):
    class Meta:
        model = EventGroup
        exclude = ['event', 'participants']
