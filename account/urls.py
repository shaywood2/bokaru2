from django.conf.urls import url
from . import views

app_name = 'account'
urlpatterns = [
    # ex: /account
    url(r'^$', views.summary, name='summary'),
    url(r'^subscription$', views.subscription, name='subscription'),
    url(r'^view$', views.view, name='view'),
    url(r'^view/(?P<username>\w+)$', views.view_user, name='view_user'),
    url(r'^edit$', views.edit, name='edit'),
    url(r'^password', views.password, name='password'),
    url(r'^notifications', views.notifications, name='notifications'),
    url(r'^closeaccount', views.closeaccount, name='closeaccount'),
    url(r'^history', views.history, name='history'),
    url(r'^settings$', views.settings, name='settings'),
    url(r'^close$', views.close, name='close'),
    url(r'^payment$', views.payment, name='payment'),
]
