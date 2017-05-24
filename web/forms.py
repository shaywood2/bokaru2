from django.forms import ModelForm
from django import forms
from datetime import date
from django.forms import widgets

from .models import Event, EventGroup


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ['creator', 'product']

    startDateTime = forms.SplitDateTimeField(widget=forms.SplitHiddenDateTimeWidget(), input_time_formats=['%H:%M'],
                                             input_date_formats=['%d.%m.%Y'])


class EventGroupForm(ModelForm):
    class Meta:
        model = EventGroup
        exclude = ['event', 'participants']


