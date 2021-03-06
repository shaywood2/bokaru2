import base64
import io
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from stripe import CardError

from event.models import Pick
from money.model_transaction import Transaction
from money.models import UserPaymentInfo
from .forms import AccountForm, UserPreferenceForm
from .models import Account, UserPreference, Memo

LOGGER = logging.getLogger(__name__)


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

    context = {
        'user': current_user,
        'account': account,
        'profile_incomplete': profile_incomplete,
        'profile_suspended': profile_suspended
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

            image_data = form.cleaned_data['image_data']

            # Add photo
            if image_data and len(image_data) > 0:
                img_format, img_data = image_data.split(';base64,')
                byte_stream = io.BytesIO(base64.b64decode(img_data))
                account.add_photo(byte_stream, 400)

                request.session['photo_url'] = account.photo.url
                request.session['thumbnail_url'] = account.photoThumbnail.url

            # Update session
            request.session['profile_incomplete'] = account.status == Account.CREATED

            return HttpResponseRedirect(reverse('account:view'))
    else:
        form = AccountForm(instance=account)

    photo_url = None
    if account.photo is not None and account.photo.name != '':
        photo_url = account.photo.url

    return render(request, 'account/edit.html', {'form': form, 'photo_url': photo_url, 'email': current_user.email})


@login_required
def preferences(request):
    current_user = request.user
    preference = UserPreference.objects.get(user=current_user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()

            messages.add_message(request, messages.SUCCESS, 'Changes saved!')

            return HttpResponseRedirect(reverse('account:preferences'))
    else:
        form = UserPreferenceForm(instance=preference)

    return render(request, 'account/preferences.html', {'form': form})


@login_required
def preferences_payment(request):
    current_user = request.user

    if request.method == 'POST':
        token = request.POST['stripeToken']

        try:
            UserPaymentInfo.objects.create_or_update_credit_card(current_user, token)
        except CardError as ce:
            body = ce.json_body
            err = body.get('error', {})

            LOGGER.error(err.get('message'))
            messages.add_message(request, messages.ERROR, 'We could not register this card for the following reason: '
                                 + str(err.get('message')))
        except Exception as e:
            LOGGER.error(str(e))
            messages.add_message(request, messages.ERROR, 'We could not register this card!'
                                                          ' Please try again or use a different card.')

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
