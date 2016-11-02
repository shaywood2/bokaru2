from django.shortcuts import get_object_or_404, render


def summary(request):
    context = {
        'test': "Summary Page",
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
