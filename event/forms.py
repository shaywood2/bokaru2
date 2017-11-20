from django import forms
from django.forms import ModelForm

from .models import Event, EventGroup


class EventForm(ModelForm):
    # Photo cropping fields
    upload_image = forms.ImageField(required=False)
    crop_x = forms.FloatField(widget=forms.HiddenInput())
    crop_y = forms.FloatField(widget=forms.HiddenInput())
    crop_w = forms.FloatField(widget=forms.HiddenInput())
    crop_h = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Event
        exclude = ['creator', 'product', 'locationCoordinates']

    startDateTime = forms.SplitDateTimeField(widget=forms.SplitHiddenDateTimeWidget(), input_time_formats=['%H:%M'],
                                             input_date_formats=['%d.%m.%Y'])


class EventGroupForm(ModelForm):
    class Meta:
        model = EventGroup
        exclude = ['event', 'participants']
