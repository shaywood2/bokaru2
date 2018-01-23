import logging
from datetime import datetime
from datetime import timedelta

from django import forms
from django.utils.dateparse import parse_time
from django.utils.translation import ugettext_lazy as _

from .models import Event, EventGroup

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Basic info
class CreateEventStep1(forms.Form):
    error_messages = {
        'too_soon': _('The event must start at least 48 hours from now.'),
        'too_late': _('The event must is too far in the future,'
                      ' please make sure that it starts within the next 90 days.'),
        'location_not_found': _('Location was not found, please update it to something that Google knows.')
    }

    TIME_CHOICES = [
        ('00:00', '12:00 AM'),
        ('00:30', '12:30 AM'),
        ('01:00', '1:00 AM'),
        ('01:30', '1:30 AM'),
        ('02:00', '2:00 AM'),
        ('02:30', '2:30 AM'),
        ('03:00', '3:00 AM'),
        ('03:30', '3:30 AM'),
        ('04:00', '4:00 AM'),
        ('04:30', '4:30 AM'),
        ('05:00', '5:00 AM'),
        ('05:30', '5:30 AM'),
        ('06:00', '6:00 AM'),
        ('06:30', '6:30 AM'),
        ('07:00', '7:00 AM'),
        ('07:30', '7:30 AM'),
        ('08:00', '8:00 AM'),
        ('08:30', '8:30 AM'),
        ('09:00', '9:00 AM'),
        ('09:30', '9:30 AM'),
        ('10:00', '10:00 AM'),
        ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'),
        ('11:30', '11:30 AM'),
        ('12:00', '12:00 PM'),
        ('12:30', '12:30 PM'),
        ('13:00', '1:00 PM'),
        ('13:30', '1:30 PM'),
        ('14:00', '2:00 PM'),
        ('14:30', '2:30 PM'),
        ('15:00', '3:00 PM'),
        ('15:30', '3:30 PM'),
        ('16:00', '4:00 PM'),
        ('16:30', '4:30 PM'),
        ('17:00', '5:00 PM'),
        ('17:30', '5:30 PM'),
        ('18:00', '6:00 PM'),
        ('18:30', '6:30 PM'),
        ('19:00', '7:00 PM'),
        ('19:30', '7:30 PM'),
        ('20:00', '8:00 PM'),
        ('20:30', '8:30 PM'),
        ('21:00', '9:00 PM'),
        ('21:30', '9:30 PM'),
        ('22:00', '10:00 PM'),
        ('22:30', '10:30 PM'),
        ('23:00', '11:00 PM'),
        ('23:30', '11:30 PM')
    ]

    name = forms.CharField(max_length=150)
    type = forms.ChoiceField(choices=Event.TYPES, initial=Event.SERIOUS)
    date = forms.DateField()
    time = forms.ChoiceField(choices=TIME_CHOICES, initial='19:00')
    locationName = forms.CharField(max_length=150)

    # Additional location fields
    cityName = forms.CharField(widget=forms.HiddenInput(), required=False)
    cityLat = forms.FloatField(widget=forms.HiddenInput(), required=False)
    cityLng = forms.FloatField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super(CreateEventStep1, self).clean()

        # Validate start time
        start_date = cleaned_data.get('date')
        start_time = cleaned_data.get('time')

        if start_date is None or start_time is None:
            return None

        start_time = parse_time(start_time)
        start_date = datetime.combine(start_date, start_time)
        tomorrow = datetime.now() + timedelta(hours=48)
        latest_date = datetime.now() + timedelta(days=90)

        if start_date < tomorrow:
            raise forms.ValidationError(
                self.error_messages['too_soon'],
                code='too_soon'
            )

        if start_date > latest_date:
            raise forms.ValidationError(
                self.error_messages['too_late'],
                code='too_late'
            )

        # Validate location
        city_name = cleaned_data.get('cityName')
        if not city_name or len(city_name) == 0:
            raise forms.ValidationError(
                self.error_messages['location_not_found'],
                code='location_not_found'
            )

        return cleaned_data


# Description
class CreateEventStep2(forms.Form):
    description = forms.CharField(widget=forms.Textarea, max_length=2000)


# Number of groups
class CreateEventStep3(forms.Form):
    SIZE_CHOICES = [
        (Event.SMALL, 'Small'),
        (Event.MEDIUM, 'Medium'),
        (Event.LARGE, 'Large')
    ]
    numGroups = forms.IntegerField(widget=forms.HiddenInput())
    eventSize = forms.ChoiceField(choices=SIZE_CHOICES, initial=Event.MEDIUM)


# Group details
class CreateEventStep4a(forms.Form):
    sexualIdentity = forms.ChoiceField(choices=EventGroup.IDENTITY_CHOICES)
    sexualIdentityOther = forms.CharField(max_length=150, required=False)
    ageMin = forms.IntegerField(widget=forms.HiddenInput(), min_value=18, initial=22)
    ageMax = forms.IntegerField(widget=forms.HiddenInput(), min_value=18, initial=99)


# Group details (2 groups)
class CreateEventStep4b(forms.Form):
    sexualIdentity1 = forms.ChoiceField(choices=EventGroup.IDENTITY_CHOICES, initial='female')
    sexualIdentityOther1 = forms.CharField(max_length=150, required=False)
    ageMin1 = forms.IntegerField(widget=forms.HiddenInput(), min_value=18, initial=22)
    ageMax1 = forms.IntegerField(widget=forms.HiddenInput(), min_value=18, initial=99)

    sexualIdentity2 = forms.ChoiceField(choices=EventGroup.IDENTITY_CHOICES, initial='male')
    sexualIdentityOther2 = forms.CharField(max_length=150, required=False)
    ageMin2 = forms.IntegerField(widget=forms.HiddenInput(), min_value=18, initial=22)
    ageMax2 = forms.IntegerField(widget=forms.HiddenInput(), min_value=18, initial=99)


# Image
class CreateEventStep5(forms.Form):
    image_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    image_data = forms.CharField(widget=forms.HiddenInput(), required=False)


# Preview
class CreateEventStep6(forms.Form):
    pass
