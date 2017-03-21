from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date

from registration.backends.hmac.views import RegistrationView as BaseRegistrationView

from .forms import RegistrationForm, AccountForm
from .models import Account


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


def payment(request):
    context = {
        'test': "Payment Page",
    }

    return render(request, 'account/payment.html', context)
