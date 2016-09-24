from django.conf.urls import url

from . import views

app_name = 'web'
urlpatterns = [
    # ex: /chat/session
    url(r'^$', views.index, name='index'),
]
