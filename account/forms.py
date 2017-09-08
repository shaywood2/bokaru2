import io
import logging

from PIL import Image
from django import forms
from django.core.files.storage import default_storage
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail

from .models import Account

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RegistrationForm(RegistrationFormUniqueEmail):
    error_messages = {
        'email_mismatch': _('The two email fields didn\'t match.'),
        'password_mismatch': _('The two password fields didn\'t match.'),
    }

    fullName = forms.CharField(max_length=150)
    email2 = forms.EmailField(required=True)
    terms = forms.BooleanField(error_messages={'required': _(u'You must agree to the terms to register')})
    newsletter = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(RegistrationFormUniqueEmail, self).__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({'placeholder': _(u'Your username'), 'autofocus': ''})
        if 'fullName' in self.fields:
            self.fields['fullName'].widget.attrs.update({'placeholder': _(u'Your name')})
        if 'email' in self.fields:
            self.fields['email'].widget.attrs.update({'placeholder': _(u'Your email')})
        if 'email2' in self.fields:
            self.fields['email2'].widget.attrs.update({'placeholder': _(u'Confirm email')})
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
                code='password_mismatch',
            )
        return password2

    def clean_email2(self):
        # Emails must match
        email1 = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError(
                self.error_messages['email_mismatch'],
                code='email_mismatch',
            )
        return email2

    def save(self, commit=True):
        user = super(RegistrationFormUniqueEmail, self).save(commit=False)
        if commit:
            user.save()
        return user


class AccountForm(ModelForm):
    # Photo cropping fields
    crop_x = forms.FloatField(widget=forms.HiddenInput())
    crop_y = forms.FloatField(widget=forms.HiddenInput())
    crop_w = forms.FloatField(widget=forms.HiddenInput())
    crop_h = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Account
        exclude = ['user', 'locationCoordinates']

    def save(self, commit=True):
        account = super(AccountForm, self).save(commit=False)

        if commit:
            account.save()

        # Get cropping parameters
        x = self.cleaned_data.get('crop_x')
        y = self.cleaned_data.get('crop_y')
        w = self.cleaned_data.get('crop_w')
        h = self.cleaned_data.get('crop_h')

        # Open the image file and read as an image
        file = default_storage.open(account.photo.path, 'rb')
        image = Image.open(file)

        # Crop and resize the image
        cropped_image = image.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((400, 400), Image.ANTIALIAS)

        # Create a binary stream
        stream = io.BytesIO()
        resized_image.save(stream, 'JPEG')
        file.close()

        # Reopen the file for writing
        file = default_storage.open(account.photo.path, 'wb')
        file.write(stream.getvalue())
        file.close()

        return account
