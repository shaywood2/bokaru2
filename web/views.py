

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render


def index(request):
    context = {
        'test': "Index Page",
    }

    return render(request, 'web/index.html', context)


def test(request):
    context = {
        'test': "Test Page",
    }

    return render(request, 'web/test.html', context)


def login(request):
    context = {
        'test': "Login Page",
    }

    return render(request, 'web/login.html', context)


def register(request):
    context = {
        'test': "Register Page",
    }

    return render(request, 'web/register.html', context)


def search(request):
    context = {
        'test': "Search Page",
    }

    return render(request, 'web/search.html', context)


def results(request):
    context = {
        'test': "Search Results Page",
    }

    return render(request, 'web/results.html', context)


def event(request):
    context = {
        'test': "Event Detail Page",
    }

    return render(request, 'web/event.html', context)


def eventcreate(request):
    context = {
        'test': "Event Create Page",
    }

    return render(request, 'web/eventcreate.html', context)


def eventedit(request):
    context = {
        'test': "Event Edit Page",
    }

    return render(request, 'web/eventedit.html', context)



def participants(request):
    context = {
        'test': "Event Participants Page",
    }

    return render(request, 'web/participants.html', context)


def eventjoined(request):
    context = {
        'test': "Event Joined Page",
    }

    return render(request, 'web/eventjoined.html', context)


def matches(request):
    context = {
        'test': "My Matches Page",
    }

    return render(request, 'web/matches.html', context)


def myevents(request):
    context = {
        'test': "My Events Page",
    }

    return render(request, 'web/myevents.html', context)


def termsofuse(request):
    context = {
        'test': "Terms of Use Page",
    }

    return render(request, 'web/termsofuse.html', context)


def howitworks(request):
    context = {
        'test': "How It Works Page",
    }

    return render(request, 'web/howitworks.html', context)


def privacypolicy(request):
    context = {
        'test': "Privacy Policy Page",
    }

    return render(request, 'web/privacypolicy.html', context)



