import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from registration.backends.hmac.views import RegistrationView as BaseRegistrationView

from money.models import UserPaymentInfo
from money.model_transaction import Transaction
from event.models import Pick
from .forms import RegistrationForm, AccountForm, UserPreferenceForm, PhotoForm
from .models import Account, UserPreference, Memo

LOGGER = logging.getLogger(__name__)


# Custom view for registration page
class RegistrationView(BaseRegistrationView):
    form_class = RegistrationForm

    def register(self, form):
        new_user = BaseRegistrationView.register(self, form)
        # Create account object
        acc = Account()
        acc.fullName = form.cleaned_data['fullName']
        acc.user = new_user
        acc.status = Account.CREATED
        acc.save()

        # Create user preferences object
        pref = UserPreference()
        pref.user = new_user
        pref.receiveNewsletter = form.cleaned_data.get('newsletter')
        # Set Toronto as default search location
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


# Listen to login signal and put account into session
def stuff_session(sender, user, request, **kwargs):
    try:
        account = Account.objects.get(user=user)
        if account.photo is not None and account.photo.name != '':
            request.session['photo_url'] = account.photo.url
            request.session['thumbnail_url'] = account.photoThumbnail.url

        request.session['profile_incomplete'] = account.status == Account.CREATED
        request.session['profile_suspended'] = account.status == Account.SUSPENDED
    except Account.DoesNotExist:
        return


user_logged_in.connect(stuff_session)


@login_required
def view(request):
    current_user = request.user
    account = Account.objects.get(user=current_user)
    profile_incomplete = account.status == Account.CREATED
    profile_suspended = account.status == Account.SUSPENDED
    photo_form = PhotoForm()

    context = {
        'user': current_user,
        'account': account,
        'profile_incomplete': profile_incomplete,
        'profile_suspended': profile_suspended,
        'photo_form': photo_form
    }

    return render(request, 'account/view.html', context)


def view_user(request, username):
    current_user = request.user
    user = get_object_or_404(User, username=username)
    account = Account.objects.get(user=user)
    profile_incomplete = account.status == Account.CREATED
    profile_suspended = account.status == Account.SUSPENDED
    can_contact = False
    show_memo = False
    memo = None

    if current_user.is_authenticated:
        can_contact = Pick.objects.is_match(current_user, user)
        show_memo = True

        # Get memo text
        memo = Memo.objects.get_memo_content(current_user, user)

        # Redirect to view own profile
        if current_user.id == user.id:
            return HttpResponseRedirect(reverse('account:view'))

    context = {
        'user': user,
        'account': account,
        'profile_incomplete': profile_incomplete,
        'profile_suspended': profile_suspended,
        'can_contact': can_contact,
        'show_memo': show_memo,
        'memo': memo
    }

    return render(request, 'account/view_user.html', context)


@login_required
def edit(request):
    current_user = request.user
    account = Account.objects.get(user=current_user)

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()

            # Update session
            request.session['profile_incomplete'] = account.status == Account.CREATED

            return HttpResponseRedirect(reverse('account:view'))
    else:
        form = AccountForm(instance=account)

    photo_url = None
    if account.photo is not None and account.photo.name != '':
        photo_url = account.photo.url

    return render(request, 'account/edit.html', {'form': form, 'photo_url': photo_url, 'email': current_user.email})


@login_required()
def update_photo(request):
    current_user = request.user
    account = Account.objects.get(user=current_user)

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['upload_image'].read()

            # Get cropping parameters
            x = form.cleaned_data.get('crop_x')
            y = form.cleaned_data.get('crop_y')
            w = form.cleaned_data.get('crop_w')
            h = form.cleaned_data.get('crop_h')

            account.add_photo(image_file, x, y, w, h, 400)

            # Update image in session
            request.session['thumbnail_url'] = account.photoThumbnail.url

    # Redirect to edit profile page
    return HttpResponseRedirect(reverse('account:view'))


@login_required
def preferences(request):
    current_user = request.user
    preference = UserPreference.objects.get(user=current_user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            # Redirect to view profile page
            return HttpResponseRedirect(reverse('account:view'))
    else:
        form = UserPreferenceForm(instance=preference)

    return render(request, 'account/preferences.html', {'form': form})


@login_required
def preferences_payment(request):
    current_user = request.user

    if request.method == 'POST':
        token = request.POST['stripeToken']

        UserPaymentInfo.objects.create_or_update_credit_card(current_user, token)

        return HttpResponseRedirect(reverse('account:payment'))
    else:
        # Retrieve the payment information for the user
        credit_card = UserPaymentInfo.objects.find_credit_card_by_user(current_user)

        return render(request, 'account/preferences_payment.html', {
            'credit_card': credit_card,
            'stripe_secret': settings.STRIPE_SECRET
        })


@login_required
def preferences_payment_history(request):
    current_user = request.user

    # Retrieve the payment history for the user
    transactions = Transaction.objects.get_history_for_user(current_user)
    remaining_credit = Transaction.objects.get_credit_for_user(current_user)

    return render(request, 'account/preferences_payment_history.html', {
        'transactions': transactions,
        'remaining_credit': float(remaining_credit) / 100
    })


@login_required
def close(request):
    current_user = request.user

    if request.method == 'POST':
        current_user.is_active = False
        current_user.save()
        # TODO: drop out of all events
        return HttpResponseRedirect(reverse('web:index'))
    else:
        return render(request, 'account/preferences_close_account.html')


@login_required
def create_or_update_memo(request, about_user_id):
    if request.method == 'POST':
        # Get content from the body
        content = request.body.decode('utf-8')
        memo = Memo.objects.create_or_update_memo_by_id(request.user, about_user_id, content)

        return JsonResponse({'owner': str(memo.owner), 'about': str(memo.about), 'content': str(memo.content)})
