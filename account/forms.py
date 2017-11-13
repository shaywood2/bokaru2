import logging

from django import forms
from django.contrib.gis.geos import Point
from django.forms import ModelForm
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

    def __init__(self, *args, **kwargs):
        super(RegistrationFormUniqueEmail, self).__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({'placeholder': _(u'Your username'), 'autofocus': ''})
        if 'fullName' in self.fields:
            self.fields['fullName'].widget.attrs.update({'placeholder': _(u'Your name')})
        if 'email' in self.fields:
            self.fields['email'].widget.attrs.update({'placeholder': _(u'Your email')})
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'placeholder': _(u'Enter password')})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'placeholder': _(u'Confirm password')})

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
        'at_least_one_required': _('Please select at least one.'),
    }

    contactInfo = forms.CharField(max_length=150, widget=forms.Textarea(
        attrs={'class': 'form-control form-control-md u-textarea-expandable rounded-0'}))
    summary = forms.CharField(max_length=2000, widget=forms.Textarea(
        attrs={'class': 'form-control form-control-md u-textarea-expandable rounded-0'}))
    # Additional location fields
    cityName = forms.CharField(widget=forms.HiddenInput())
    cityLat = forms.FloatField(widget=forms.HiddenInput())
    cityLng = forms.FloatField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        # Making fields required
        self.fields['fullName'].required = True
        self.fields['birthDate'].required = True
        self.fields['lookingForAgeMin'].required = True
        self.fields['lookingForAgeMax'].required = True

        # Add styles
        self.fields['fullName'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0'})
        self.fields['locationName'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0'})
        self.fields['sexualIdentity'].widget.attrs.update(
            {'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['sexualIdentityOther'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0'})
        self.fields['sexualOrientation'].widget.attrs.update(
            {'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['sexualOrientationOther'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0'})
        self.fields['birthDate'].widget.attrs.update(
            {'class': 'form-control form-control-md u-datepicker-v1 g-brd-right-none rounded-0'})
        self.fields['relationshipStatus'].widget.attrs.update(
            {'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['relationshipType'].widget.attrs.update(
            {'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['height'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0'})
        self.fields['bodyType'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})

        self.fields['ethnicityList'].widget.attrs.update({'style': 'display: none'})
        self.fields['languageList'].widget.attrs.update({'style': 'display: none'})
        self.fields['education'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['religion'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})

        self.fields['viceSmoking'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['viceDrinking'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['viceDrugs'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['diet'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['kidsHave'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['kidsWant'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0 u-select-v1'})
        self.fields['petList'].widget.attrs.update({'style': 'display: none'})

        self.fields['lookingForGenderList'].widget.attrs.update({'style': 'display: none'})
        self.fields['lookingForAgeMin'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0'})
        self.fields['lookingForAgeMax'].widget.attrs.update({'class': 'form-control rounded-0 u-form-control0'})
        self.fields['lookingForConnectionsList'].widget.attrs.update({'style': 'display: none'})

    class Meta:
        model = Account
        exclude = ['user', 'status', 'locationCoordinates']

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

    def save(self):
        # Save coordinates
        lat = self.cleaned_data.get('cityLat')
        lng = self.cleaned_data.get('cityLng')

        point = self.instance.locationCoordinates
        point.set_x(lat)
        point.set_y(lng)

        super(AccountForm, self).save()


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
        exclude = ['user', 'locationCoordinates']
