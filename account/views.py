from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date

from registration.backends.hmac.views import RegistrationView as BaseRegistrationView
import stripe

from .forms import RegistrationForm, AccountForm
from .models import Account, Payment


class RegistrationView(BaseRegistrationView):
    form_class = RegistrationForm

    def register(self, form):
        new_user = BaseRegistrationView.register(self, form)
        acc = Account()
        acc.fullName = form.cleaned_data['fullName']
        acc.user = new_user
        acc.status = 'created'
        acc.save()


@login_required
def summary(request):
    try:
        acc = Account.objects.get(user=request.user)
    except:
        acc = None

    context = {
        'test': "Summary Page",
        'user': request.user,
        'account': acc
    }

    return render(request, 'account/summary.html', context)


def subscription(request):
    context = {
        'test': "Subscription Page",
    }

    return render(request, 'account/subscription.html', context)


@login_required
def view(request):
    current_user = request.user
    account = Account.objects.get(user=current_user)

    if account.birthDate is not None:
        age = calculate_age(account.birthDate)
        account.age = age

    context = {
        'user': current_user,
        'account': account,

    }

    return render(request, 'account/view.html', context)


def calculate_age(born):
    today = date.today()
    years_difference = today.year - born.year
    is_before_birthday = (today.month, today.day) < (born.month, born.day)
    elapsed_years = years_difference - int(is_before_birthday)
    return elapsed_years


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
            # Redirect to view profile page
            return HttpResponseRedirect(reverse('account:view'))
    else:
        form = AccountForm(instance=account)

    return render(request, 'account/edit.html', {'form': form})


def password(request):
    context = {}

    return render(request, 'account/changepassword.html', context)


def notifications(request):
    context = {}

    return render(request, 'account/notifications.html', context)


def closeaccount(request):
    context = {}

    return render(request, 'account/close.html', context)


def history(request):
    context = {}

    return render(request, 'account/history.html', context)


def settings(request):
    context = {
        'test': "Account Settings Page",
    }

    return render(request, 'account/settings.html', context)


def close(request):
    context = {
        'test': "Close Account Page",
    }

    return render(request, 'account/close.html', context)


@login_required
def payment(request):
    return render(request, 'account/payment.html')


@login_required
def payment_create(request):
    current_user = request.user
    stripe.api_key = "sk_test_28uxXqhjVInC6y28EXbq84je"

    # Get the credit card details submitted by the form
    token = request.POST['stripeToken']

    # Create a Customer
    customer = stripe.Customer.create(
        source=token,
        description=current_user.first_name + ' ' + current_user.last_name,
        email=current_user.email,
        metadata={'user_id': current_user.id}
    )

    # Store the customer id
    p, created = Payment.objects.get_or_create(
        user=current_user,
        defaults={'stripe_customer_id': customer.id}
    )

    # Create a charge
    # stripe.Charge.create(
    #     amount=1500,  # $15.00 this time
    #     currency="cad",
    #     customer=customer_id  # Previously stored, then retrieved
    # )

    context = {
        'payment': p,
        'created': created
    }

    return render(request, 'account/payment_success.html', context)
