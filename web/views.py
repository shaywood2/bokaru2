from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required


def index(request):
    template = loader.get_template('web/index.html')
    context = {
        'user': request.user,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="web:login")
def account(request):
    template = loader.get_template('web/account.html')
    context = {
        'user': request.user,
    }
    return HttpResponse(template.render(context, request))
