from django import forms
from django.forms import Form
from django.forms import ModelForm

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


class SearchForm(Form):
    search_term = forms.CharField(label='Search text', max_length=100)
    distance = forms.IntegerField(label='Distance from your location', max_value=100, required=False)
