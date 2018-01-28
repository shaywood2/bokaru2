import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from bokaru.email import send_email
from money.model_transaction import Transaction
from .forms import RegistrationForm, RegistrationAndJoinForm
from .models import Account, UserPreference

LOGGER = logging.getLogger(__name__)
REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = __create_inactive_user(form, request)

            # Create account object
            acc = Account()
            acc.fullName = form.cleaned_data['fullName']
            acc.user = new_user
            acc.status = Account.CREATED
            acc.save()

            return HttpResponseRedirect(reverse('account:registration_success'))
    else:
        form = RegistrationForm()

    return render(request, 'registration/registration_form.html', {'form': form})


def register_success(request):
    return render(request, 'registration/registration_complete.html')


def activate(request, activation_key):
    data = __validate_key(activation_key)

    if data is None:
        return render(request, 'registration/activation_failed.html')

    username = data.get('username')
    group_id = data.get('group_id')

    if username is not None:
        user = __get_user(username)
        if user is not None:
            user.is_active = True
            user.save()

            if group_id is not None:
                messages.add_message(request, messages.SUCCESS,
                                     'Your account is activated! Please log on to join the event.')
                return HttpResponseRedirect(reverse('event:join', kwargs={'group_id': group_id}))
            else:
                return render(request, 'registration/activation_complete.html')

    return render(request, 'registration/activation_failed.html')


def register_and_join_group(request, group_id):
    if request.method == 'POST':
        form = RegistrationAndJoinForm(request.POST)
        if form.is_valid():
            new_user = __create_inactive_user(form, request, group_id)

            # Create account object
            acc = Account()
            acc.fullName = form.cleaned_data['fullName']

            acc.locationName = form.cleaned_data['locationName']
            acc.birthDate = form.cleaned_data['birthDate']
            acc.sexualOrientation = form.cleaned_data['sexualOrientation']
            acc.sexualOrientationOther = form.cleaned_data['sexualOrientationOther']
            acc.sexualIdentity = form.cleaned_data['sexualIdentity']
            acc.sexualIdentityOther = form.cleaned_data['sexualIdentityOther']
            acc.lookingForGenderList = form.cleaned_data['lookingForGenderList']
            acc.lookingForAgeMin = form.cleaned_data['lookingForAgeMin']
            acc.lookingForAgeMax = form.cleaned_data['lookingForAgeMax']
            acc.lookingForConnectionsList = form.cleaned_data['lookingForConnectionsList']

            # Save coordinates
            lat = form.cleaned_data.get('cityLat')
            lng = form.cleaned_data.get('cityLng')

            if lat and lng:
                point = acc.locationCoordinates
                point.x = lng
                point.y = lat

            acc.user = new_user
            acc.status = Account.COMPLETED
            acc.save()

            return HttpResponseRedirect(reverse('account:registration_success'))
        else:
            LOGGER.error(str(form.errors))
    else:
        form = RegistrationAndJoinForm()

    return render(request, 'registration/registration_and_join_form.html', {'form': form})


def __create_inactive_user(form, request, group_id=None):
    """
    Create the inactive user account and send an email containing
    activation instructions.

    """
    new_user = form.save(commit=False)
    new_user.is_active = False
    new_user.save()

    # Create user preferences object
    pref = UserPreference()
    pref.user = new_user
    pref.receiveNewsletter = form.cleaned_data.get('newsletter')
    pref.timezoneName = form.cleaned_data.get('timezoneName')
    # Set Toronto as the default search location
    pref.cityName = 'Toronto, ON, Canada'
    pref.cityNameShort = 'Toronto'
    pref.cityLat = 43.653226
    pref.cityLng = -79.3831843
    pref.save()

    # Apply welcome credit
    credit_amount = getattr(settings, 'WELCOME_CREDIT', 0)
    credit_description = getattr(settings, 'WELCOME_CREDIT_TEXT', 'Bonus site credit')
    if credit_amount > 0:
        Transaction.objects.apply_welcome_credit(new_user, credit_amount, credit_description)

    LOGGER.info('Registered a new user: {!s}. Bonus credit amount: {:d}'.format(new_user, credit_amount))

    __send_activation_email(new_user, credit_amount, request, group_id)

    return new_user


def __send_activation_email(user, credit_amount, request, group_id):
    """
    Send the activation email. The activation key is the username,
    signed using TimestampSigner.

    """
    data = {
        'username': getattr(user, user.USERNAME_FIELD),
        'group_id': group_id
    }

    activation_key = signing.dumps(
        obj=data,
        salt=REGISTRATION_SALT
    )

    email_context = {
        'activation_key': activation_key,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        'credit_amount': credit_amount,
        'site': get_current_site(request),
        'user': user,
    }
    send_email(user.email, email_context, 'activation')


def __validate_key(activation_key):
    """
    Verify that the activation key is valid and within the
    permitted activation time window, returning the username if
    valid or ``None`` if not.

    """
    try:
        data = signing.loads(
            activation_key,
            salt=REGISTRATION_SALT,
            max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
        )
        return data
    # SignatureExpired is a subclass of BadSignature, so this will
    # catch either one.
    except signing.BadSignature:
        return None


def __get_user(username):
    """
    Given the verified username, look up and return the
    corresponding user account if it exists, or ``None`` if it
    doesn't.

    """
    try:
        user = get_user_model().objects.get(**{
            get_user_model().USERNAME_FIELD: username,
            'is_active': False
        })
        return user
    except get_user_model().DoesNotExist:
        return None
