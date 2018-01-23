import logging

from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail

from .models import Account, UserPreference

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RegistrationForm(RegistrationFormUniqueEmail):
    error_messages = {
        'password_mismatch': _('The two password fields didn\'t match.'),
        'terms_required': _('You must agree to the terms to register.'),
    }

    fullName = forms.CharField(max_length=150)
    terms = forms.BooleanField(required=False)
    newsletter = forms.BooleanField(required=False)

    def clean_password2(self):
        # Passwords must match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch'
            )
        return password2

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms:
            raise forms.ValidationError(
                self.error_messages['terms_required'],
                code='terms_required'
            )
        return terms

    def save(self, commit=True):
        user = super(RegistrationFormUniqueEmail, self).save(commit=False)
        if commit:
            user.save()
        return user


class AccountForm(ModelForm):
    error_messages = {
        'details_required': _('Please provide more details.'),
        'age_range_error': _('Maximum age should be greater than the minimum age.'),
        'at_least_one_required': _('Please select at least one item.'),
        'under_18': _('You must be older than 18 to register.'),
        'location_not_found': _('Location was not found, please update it to something that Google knows.')
    }

    # Change widget type to TextArea
    contactInfo = forms.CharField(max_length=150, required=False, widget=forms.Textarea())
    summary = forms.CharField(max_length=2000, required=False, widget=forms.Textarea())

    # Additional fields
    cityName = forms.CharField(widget=forms.HiddenInput(), required=False)
    cityLat = forms.FloatField(widget=forms.HiddenInput(), required=False)
    cityLng = forms.FloatField(widget=forms.HiddenInput(), required=False)
    image_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    image_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        # Making fields required
        self.fields['fullName'].required = True
        self.fields['birthDate'].required = True
        self.fields['sexualOrientation'].required = True
        self.fields['sexualIdentity'].required = True

        # Hide fields
        self.fields['lookingForAgeMin'].widget = forms.HiddenInput()
        self.fields['lookingForAgeMax'].widget = forms.HiddenInput()
        self.fields['ethnicityList'].widget = forms.HiddenInput()
        self.fields['languageList'].widget = forms.HiddenInput()
        self.fields['petList'].widget = forms.HiddenInput()
        self.fields['lookingForGenderList'].widget = forms.HiddenInput()
        self.fields['lookingForConnectionsList'].widget = forms.HiddenInput()

    class Meta:
        model = Account
        exclude = ['user', 'status', 'locationCoordinates']

    def clean_birthDate(self):
        birth_date = self.cleaned_data.get('birthDate')

        if birth_date is None:
            return None

        today = timezone.now()
        years_difference = today.year - birth_date.year
        is_before_birthday = (today.month, today.day) < (birth_date.month, birth_date.day)
        elapsed_years = years_difference - int(is_before_birthday)
        if elapsed_years < 18:
            raise forms.ValidationError(
                self.error_messages['under_18'],
                code='under_18'
            )

        return birth_date

    def clean_sexualIdentityOther(self):
        si = self.cleaned_data.get('sexualIdentity')
        sio = self.cleaned_data.get('sexualIdentityOther')

        if si == 'other' and not sio:
            raise forms.ValidationError(
                self.error_messages['details_required'],
                code='details_required'
            )

        return sio

    def clean_sexualOrientationOther(self):
        so = self.cleaned_data.get('sexualOrientation')
        soo = self.cleaned_data.get('sexualOrientationOther')

        if so == 'other' and not soo:
            raise forms.ValidationError(
                self.error_messages['details_required'],
                code='details_required'
            )

        return soo

    def clean_lookingForAgeMax(self):
        age_min = self.cleaned_data.get('lookingForAgeMin')
        age_max = self.cleaned_data.get('lookingForAgeMax')

        if age_min > age_max:
            raise forms.ValidationError(
                self.error_messages['age_range_error'],
                code='age_range_error'
            )

        return age_max

    def clean_lookingForGenderList(self):
        lfg_list = self.cleaned_data.get('lookingForGenderList')

        if not lfg_list or lfg_list == '':
            raise forms.ValidationError(
                self.error_messages['at_least_one_required'],
                code='at_least_one_required'
            )

        return lfg_list

    def clean_lookingForConnectionsList(self):
        lfc_list = self.cleaned_data.get('lookingForConnectionsList')

        if not lfc_list or lfc_list == '':
            raise forms.ValidationError(
                self.error_messages['at_least_one_required'],
                code='at_least_one_required'
            )

        return lfc_list

    def clean(self):
        cleaned_data = super(AccountForm, self).clean()

        # Validate location
        if 'locationName' in self.changed_data:
            city_name = cleaned_data.get('cityName')
            if not city_name or len(city_name) == 0:
                raise forms.ValidationError(
                    self.error_messages['location_not_found'],
                    code='location_not_found'
                )

        return cleaned_data

    def save(self, commit=True):
        # Update status to completed
        if self.instance.status == Account.CREATED:
            self.instance.status = Account.COMPLETED

        # Save coordinates
        lat = self.cleaned_data.get('cityLat')
        lng = self.cleaned_data.get('cityLng')

        if lat and lng:
            point = self.instance.locationCoordinates
            point.x = lng
            point.y = lat

        super(AccountForm, self).save(commit=commit)


class PhotoForm(forms.Form):
    # Photo cropping fields
    upload_image = forms.ImageField()
    crop_x = forms.FloatField(widget=forms.HiddenInput())
    crop_y = forms.FloatField(widget=forms.HiddenInput())
    crop_w = forms.FloatField(widget=forms.HiddenInput())
    crop_h = forms.FloatField(widget=forms.HiddenInput())


class UserPreferenceForm(ModelForm):
    class Meta:
        model = UserPreference
        exclude = ['user', 'ageMin', 'ageMax', 'numGroups', 'eventType', 'eventSize']
