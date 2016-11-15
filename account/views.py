from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from registration.backends.hmac.views import RegistrationView as BaseRegistrationView

from .forms import RegistrationForm
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
    context = {
        'test': "Profile View Page",
    }

    return render(request, 'account/view.html', context)


def edit(request):
    context = {
        'test': "Profile Edit Page",
    }

    return render(request, 'account/edit.html', context)


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
