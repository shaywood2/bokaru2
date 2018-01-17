import logging

from django import forms
from django.forms import ModelForm

from account.models import UserPreference

logger = logging.getLogger(__name__)


class SearchForm(ModelForm):
    DISTANCE_CHOICES = [
        (10, 10),
        (50, 50),
        (100, 100),
        (200, 200),
        (500, 500),
    ]

    DISTANCE_UNIT_CHOICES = [
        ('km', 'Kilometers'),
        ('mi', 'Miles')
    ]

    IDENTITY_CHOICES = [
        ('female', 'Woman'),
        ('male', 'Man'),
        ('other', 'Other')
    ]

    VIEW_CHOICES = [
        ('list', 'list'),
        ('grid', 'grid')
    ]

    class Meta:
        model = UserPreference
        exclude = ['user', 'receiveNewsletter', 'created', 'updated']
        widgets = {
            'lookingForGenderList': forms.HiddenInput(),
            'lookingForAgeMin': forms.HiddenInput(),
            'lookingForAgeMax': forms.HiddenInput(),
            'eventTypeList': forms.HiddenInput(),
            'eventSizeList': forms.HiddenInput(),
            'cityNameShort': forms.HiddenInput(),
            'cityLat': forms.HiddenInput(),
            'cityLng': forms.HiddenInput(),
        }

    search_term = forms.CharField(required=False)
    sexual_identity = forms.ChoiceField(choices=IDENTITY_CHOICES, required=False)
    age = forms.IntegerField(min_value=18, widget=forms.HiddenInput(), initial=25, required=False)
    # start_date = forms.DateField(widget=forms.HiddenInput(), required=False)
    show_full = forms.BooleanField(initial=False, required=False)
    promoted_only = forms.BooleanField(initial=False, required=False)
    view_type = forms.ChoiceField(widget=forms.HiddenInput(), choices=VIEW_CHOICES, initial='list')
