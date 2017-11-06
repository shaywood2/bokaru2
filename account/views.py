from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from registration.backends.hmac.views import RegistrationView as BaseRegistrationView

from money.models import UserPaymentInfo
from money.payment_service import create_customer, delete_card, create_card
from .forms import RegistrationForm, AccountForm, UserPreferenceForm
from .models import Account, UserPreference


class RegistrationView(BaseRegistrationView):
    form_class = RegistrationForm

    def register(self, form):
        new_user = BaseRegistrationView.register(self, form)
        # Create account object
        acc = Account()
        acc.fullName = form.cleaned_data['fullName']
        acc.user = new_user
        acc.status = 'created'
        acc.save()
        # Create user preferences object
        pref = UserPreference()
        pref.user = new_user
        pref.save()


@login_required
def view(request):
    current_user = request.user
    account = Account.objects.get(user=current_user)

    context = {
        'user': current_user,
        'account': account,
    }

    return render(request, 'account/view.html', context)


def view_user(request, username):
    user = get_object_or_404(User, username=username)
    account = Account.objects.get(user=user)

    context = {
        'user': user,
        'account': account,
    }

    return render(request, 'account/view_user.html', context)


@login_required
def edit(request):
    current_user = request.user
    account = Account.objects.get(user=current_user)

    if request.method == 'POST':
        form = AccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()

            if 'upload_image' in request.FILES:
                image_file = request.FILES['upload_image'].read()

                # Get cropping parameters
                x = form.cleaned_data.get('crop_x')
                y = form.cleaned_data.get('crop_y')
                w = form.cleaned_data.get('crop_w')
                h = form.cleaned_data.get('crop_h')

                account.add_photo(image_file, x, y, w, h, 400)

            # Redirect to view profile page
            return HttpResponseRedirect(reverse('account:view'))
    else:
        form = AccountForm(instance=account)

    return render(request, 'account/edit.html', {'form': form})


@login_required
def password(request):
    context = {}

    return render(request, 'account/changepassword.html', context)


@login_required
def preferences(request):
    current_user = request.user
    preference = UserPreference.objects.get(user=current_user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, request.FILES, instance=preference)
        if form.is_valid():
            form.save()
            # Redirect to view profile page
            return HttpResponseRedirect(reverse('account:preferences'))
    else:
        form = AccountForm(instance=preference)

    return render(request, 'account/preferences.html', {'form': form})


@login_required
def history(request):
    context = {}

    return render(request, 'account/history.html', context)


@login_required
def settings(request):
    context = {
        'test': "Account Settings Page",
    }

    return render(request, 'account/settings.html', context)


@login_required
def close(request):
    context = {
        'test': "Close Account Page",
    }

    return render(request, 'account/close.html', context)


@login_required
def credit_card_view(request):
    # Retrieve the payment information for the user
    try:
        payment_info = UserPaymentInfo.objects.get(user=request.user)
        # stripe_id = payment_info.stripe_customer_id
        # LOGGER.debug('Creating a test charge')
        # create_charge(12345, 'cad', 'testing', 'cus_AQF6ZlxYXIKq0I')
        # stripe_customer = retrieve_customer(stripe_id)
        # if stripe_customer is not None:
        #    credit_card = stripe_customer.sources.data[0]
        if payment_info.has_card():
            credit_card = {
                'brand': payment_info.credit_card_brand,
                'last4': payment_info.credit_card_last_4,
                'exp_month': payment_info.credit_card_exp_month,
                'exp_year': payment_info.credit_card_exp_year,
                'id': payment_info.credit_card_id,
            }
        else:
            credit_card = None
    except UserPaymentInfo.DoesNotExist:
        credit_card = None

    return render(request, 'account/credit_card/view.html', {'credit_card': credit_card})


@login_required
def credit_card_edit(request):
    # Retrieve the payment information for the user

    return render(request, 'account/credit_card/edit.html')


@login_required
def event_pay(request, group_id):
    # Retrieve the payment information for the user
    try:
        payment_info = UserPaymentInfo.objects.get(user=request.user)
        # stripe_id = payment_info.stripe_customer_id
        # LOGGER.debug('Creating a test charge')
        # create_charge(12345, 'cad', 'testing', 'cus_AQF6ZlxYXIKq0I')
        # stripe_customer = retrieve_customer(stripe_id)
        # if stripe_customer is not None:
        #    credit_card = stripe_customer.sources.data[0]
        if payment_info.has_card():
            credit_card = {
                'brand': payment_info.credit_card_brand,
                'last4': payment_info.credit_card_last_4,
                'exp_month': payment_info.credit_card_exp_month,
                'exp_year': payment_info.credit_card_exp_year,
                'id': payment_info.credit_card_id,
            }
        else:
            credit_card = None
    except UserPaymentInfo.DoesNotExist:
        credit_card = None

    return render(request, 'account/credit_card/pay.html', {'credit_card': credit_card, 'group_id': group_id})


@login_required
def credit_card_register(request):
    current_user = request.user
    card_found = False

    # Get the credit card details submitted by the form
    token = request.POST['stripeToken']

    try:
        # Retrieve the payment information for the user
        payment_info = UserPaymentInfo.objects.get(user=request.user)

        if payment_info.credit_card_id != 0:
            deleted = delete_card(payment_info.stripe_customer_id, payment_info.credit_card_id)

        # Create a card for an existing Customer
        credit_card = create_card(payment_info.stripe_customer_id, token)
        # Store the payment info
        payment_info.credit_card_id = credit_card.id
        payment_info.credit_card_brand = credit_card.brand
        payment_info.credit_card_last_4 = credit_card.last4
        payment_info.credit_card_exp_month = credit_card.exp_month
        payment_info.credit_card_exp_year = credit_card.exp_year
        payment_info.save()
    except UserPaymentInfo.DoesNotExist:
        # Create a Customer with a credit card
        stripe_customer = create_customer(token, current_user.id, current_user.first_name + ' '
                                          + current_user.last_name, current_user.email)

        credit_card = stripe_customer.sources.data[0]

        # Store the payment info
        payment_info, created = UserPaymentInfo.objects.get_or_create(
            user=current_user,
            defaults={'stripe_customer_id': stripe_customer.id,
                      'credit_card_id': credit_card.id,
                      'credit_card_brand': credit_card.brand,
                      'credit_card_last_4': credit_card.last4,
                      'credit_card_exp_month': credit_card.exp_month,
                      'credit_card_exp_year': credit_card.exp_year}
        )

    card = {
        'brand': payment_info.credit_card_brand,
        'last4': payment_info.credit_card_last_4,
        'exp_month': payment_info.credit_card_exp_month,
        'exp_year': payment_info.credit_card_exp_year,
        'id': payment_info.credit_card_id,
    }

    return HttpResponseRedirect(reverse('account:credit_card'))


@login_required
def credit_card_register_and_pay(request, group_id):
    current_user = request.user
    card_found = False

    # Get the credit card details submitted by the form
    token = request.POST['stripeToken']

    try:
        # Retrieve the payment information for the user
        payment_info = UserPaymentInfo.objects.get(user=request.user)

        if payment_info.credit_card_id != 0:
            deleted = delete_card(payment_info.stripe_customer_id, payment_info.credit_card_id)

        # Create a card for an existing Customer
        credit_card = create_card(payment_info.stripe_customer_id, token)
        # Store the payment info
        payment_info.credit_card_id = credit_card.id
        payment_info.credit_card_brand = credit_card.brand
        payment_info.credit_card_last_4 = credit_card.last4
        payment_info.credit_card_exp_month = credit_card.exp_month
        payment_info.credit_card_exp_year = credit_card.exp_year
        payment_info.save()
    except UserPaymentInfo.DoesNotExist:
        # Create a Customer with a credit card
        stripe_customer = create_customer(token, current_user.id, current_user.first_name + ' '
                                          + current_user.last_name, current_user.email)

        credit_card = stripe_customer.sources.data[0]

        # Store the payment info
        payment_info, created = UserPaymentInfo.objects.get_or_create(
            user=current_user,
            defaults={'stripe_customer_id': stripe_customer.id,
                      'credit_card_id': credit_card.id,
                      'credit_card_brand': credit_card.brand,
                      'credit_card_last_4': credit_card.last4,
                      'credit_card_exp_month': credit_card.exp_month,
                      'credit_card_exp_year': credit_card.exp_year}
        )

    return HttpResponseRedirect(reverse('web:event_join', kwargs={'group_id': group_id}))


@login_required
def credit_card_register_orig(request):
    current_user = request.user
    card_found = False

    # Get the credit card details submitted by the form
    token = request.POST['stripeToken']

    try:
        # Retrieve the payment information for the user
        payment_info = UserPaymentInfo.objects.get(user=request.user)
        if payment_info.has_card():
            card_found = True
        else:
            # Create a card for an existing Customer
            credit_card = create_card(payment_info.stripe_customer_id, token)
            # Store the payment info
            payment_info.credit_card_id = credit_card.id
            payment_info.credit_card_brand = credit_card.brand
            payment_info.credit_card_last_4 = credit_card.last4
            payment_info.credit_card_exp_month = credit_card.exp_month
            payment_info.credit_card_exp_year = credit_card.exp_year
            payment_info.save()
    except UserPaymentInfo.DoesNotExist:
        # Create a Customer with a credit card
        stripe_customer = create_customer(token, current_user.id, current_user.first_name + ' '
                                          + current_user.last_name, current_user.email)

        credit_card = stripe_customer.sources.data[0]

        # Store the payment info
        payment_info, created = UserPaymentInfo.objects.get_or_create(
            user=current_user,
            defaults={'stripe_customer_id': stripe_customer.id,
                      'credit_card_id': credit_card.id,
                      'credit_card_brand': credit_card.brand,
                      'credit_card_last_4': credit_card.last4,
                      'credit_card_exp_month': credit_card.exp_month,
                      'credit_card_exp_year': credit_card.exp_year}
        )

    context = {
        'payment_info': payment_info,
        'card_found': card_found
    }

    return render(request, 'account/credit_card/register_success.html', context)


@login_required
def credit_card_remove(request):
    deleted = False

    try:
        # Retrieve the payment information for the user
        payment_info = UserPaymentInfo.objects.get(user=request.user)
        if payment_info.has_card():
            deleted = delete_card(payment_info.stripe_customer_id, payment_info.credit_card_id)
            payment_info.delete_card()
            card_found = True
        else:
            card_found = False
    except UserPaymentInfo.DoesNotExist:
        card_found = False

    return render(request, 'account/credit_card/delete_card.html', {'deleted': deleted, 'card_found': card_found})
