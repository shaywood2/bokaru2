from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render


def index(request):
    context = {
        'user': request.user,
    }
    return render(request, 'web/index.html', context)


def authenticate(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return HttpResponse('true')
    else:
        # Return an 'invalid login' error message.
        return HttpResponse('false')


@login_required(login_url="web:login")
def account(request):
    context = {
        'user': request.user,
    }
    return render(request, 'web/account.html', context)
