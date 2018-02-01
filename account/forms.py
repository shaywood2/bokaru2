import logging

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import validators
from .models import Account, UserPreference

# Get an instance of a logger
logger = logging.getLogger(__name__)
User = get_user_model()


class BaseRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        help_text=_(u'email address'),
        required=True,
        validators=[
            validators.validate_confusables_email,
        ]
    )
    terms = forms.BooleanField(required=False)
    newsletter = forms.BooleanField(required=False)
    timezoneName = forms.ChoiceField(choices=UserPreference.PRETTY_TIMEZONE_CHOICES, initial=UserPreference.DEFAULT_TZ)

    class Meta(UserCreationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            'email',
            'password1',
            'password2'
        ]
        required_css_class = 'required'

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(validators.DUPLICATE_EMAIL)
        return self.cleaned_data['email']

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms:
            raise forms.ValidationError(
                validators.TOS_REQUIRED,
                code='terms_required'
            )
        return terms

    def clean(self):
        """
        Apply the reserved-name validator to the username.

        """
        username_value = self.cleaned_data.get(User.USERNAME_FIELD)
        if username_value is not None:
            try:
                if hasattr(self, 'reserved_names'):
                    reserved_names = self.reserved_names
                else:
                    reserved_names = validators.DEFAULT_RESERVED_NAMES
                reserved_validator = validators.ReservedNameValidator(
                    reserved_names=reserved_names
                )
                reserved_validator(username_value)
                validators.validate_confusables(username_value)
            except ValidationError as v:
                self.add_error(User.USERNAME_FIELD, v)
        super(BaseRegistrationForm, self).clean()


class RegistrationForm(BaseRegistrationForm):
    fullName = forms.CharField(max_length=150)

    def save(self, commit=True):
        user = super(BaseRegistrationForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class RegistrationAndJoinForm(BaseRegistrationForm):
    error_codes = {
        'password_mismatch': _('The two password fields didn\'t match.'),
        'terms_required': _('You must agree to the terms to register.'),
        'details_required': _('Please provide more details.'),
        'at_least_one_required': _('Please select at least one item.'),
        'under_18': _('You must be older than 18 to register.'),
        'location_not_found': _('Location was not found, please update it to something that Google knows.')
    }

    fullName = forms.CharField(max_length=150)

    # Profile fields
    locationName = forms.CharField(max_length=150)
    cityName = forms.CharField(widget=forms.HiddenInput(), required=False)
    cityLat = forms.FloatField(widget=forms.HiddenInput(), required=False)
    cityLng = forms.FloatField(widget=forms.HiddenInput(), required=False)
    birthDate = forms.DateField()
    sexualOrientation = forms.ChoiceField(choices=Account.ORIENTATION)
    sexualOrientationOther = forms.CharField(max_length=150, required=False)
    sexualIdentity = forms.ChoiceField(choices=Account.IDENTITY)
    sexualIdentityOther = forms.CharField(max_length=150, required=False)
    lookingForGenderList = forms.CharField(widget=forms.HiddenInput(), required=False)
    lookingForAgeMin = forms.CharField(widget=forms.HiddenInput(), required=False, initial=22)
    lookingForAgeMax = forms.CharField(widget=forms.HiddenInput(), required=False, initial=77)
    lookingForConnectionsList = forms.CharField(widget=forms.HiddenInput(), required=False)

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
                self.error_codes['under_18'],
                code='under_18'
            )

        return birth_date

    def clean_sexualIdentityOther(self):
        si = self.cleaned_data.get('sexualIdentity')
        sio = self.cleaned_data.get('sexualIdentityOther')

        if si == 'other' and not sio:
            raise forms.ValidationError(
                self.error_codes['details_required'],
                code='details_required'
            )

        return sio

    def clean_sexualOrientationOther(self):
        so = self.cleaned_data.get('sexualOrientation')
        soo = self.cleaned_data.get('sexualOrientationOther')

        if so == 'other' and not soo:
            raise forms.ValidationError(
                self.error_codes['details_required'],
                code='details_required'
            )

        return soo

    def clean_lookingForAgeMax(self):
        age_min = self.cleaned_data.get('lookingForAgeMin')
        age_max = self.cleaned_data.get('lookingForAgeMax')

        if age_min > age_max:
            raise forms.ValidationError(
                self.error_codes['age_range_error'],
                code='age_range_error'
            )

        return age_max

    def clean_lookingForGenderList(self):
        lfg_list = self.cleaned_data.get('lookingForGenderList')

        if not lfg_list or lfg_list == '':
            raise forms.ValidationError(
                self.error_codes['at_least_one_required'],
                code='at_least_one_required'
            )

        return lfg_list

    def clean_lookingForConnectionsList(self):
        lfc_list = self.cleaned_data.get('lookingForConnectionsList')

        if not lfc_list or lfc_list == '':
            raise forms.ValidationError(
                self.error_codes['at_least_one_required'],
                code='at_least_one_required'
            )

        return lfc_list

    def clean(self):
        cleaned_data = super(BaseRegistrationForm, self).clean()

        # Validate location
        if 'locationName' in self.changed_data:
            city_name = cleaned_data.get('cityName')
            if not city_name or len(city_name) == 0:
                raise forms.ValidationError(
                    self.error_codes['location_not_found'],
                    code='location_not_found'
                )

        return cleaned_data

    def save(self, commit=True):
        user = super(BaseRegistrationForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class AccountForm(ModelForm):
    error_codes = {
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
                self.error_codes['under_18'],
                code='under_18'
            )

        return birth_date

    def clean_sexualIdentityOther(self):
        si = self.cleaned_data.get('sexualIdentity')
        sio = self.cleaned_data.get('sexualIdentityOther')

        if si == 'other' and not sio:
            raise forms.ValidationError(
                self.error_codes['details_required'],
                code='details_required'
            )

        return sio

    def clean_sexualOrientationOther(self):
        so = self.cleaned_data.get('sexualOrientation')
        soo = self.cleaned_data.get('sexualOrientationOther')

        if so == 'other' and not soo:
            raise forms.ValidationError(
                self.error_codes['details_required'],
                code='details_required'
            )

        return soo

    def clean_lookingForAgeMax(self):
        age_min = self.cleaned_data.get('lookingForAgeMin')
        age_max = self.cleaned_data.get('lookingForAgeMax')

        if age_min > age_max:
            raise forms.ValidationError(
                self.error_codes['age_range_error'],
                code='age_range_error'
            )

        return age_max

    def clean_lookingForGenderList(self):
        lfg_list = self.cleaned_data.get('lookingForGenderList')

        if not lfg_list or lfg_list == '':
            raise forms.ValidationError(
                self.error_codes['at_least_one_required'],
                code='at_least_one_required'
            )

        return lfg_list

    def clean_lookingForConnectionsList(self):
        lfc_list = self.cleaned_data.get('lookingForConnectionsList')

        if not lfc_list or lfc_list == '':
            raise forms.ValidationError(
                self.error_codes['at_least_one_required'],
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
                    self.error_codes['location_not_found'],
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


class UserPreferenceForm(ModelForm):
    class Meta:
        model = UserPreference
        exclude = ['user', 'ageMin', 'ageMax', 'numGroups', 'eventType', 'eventSize',
                   'lookingForAgeMin', 'lookingForAgeMax', 'distance']
