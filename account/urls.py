from django.conf.urls import url
from . import views

app_name = 'account'
urlpatterns = [
    # ex: /profile
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
    url(r'^credit_card$', views.credit_card_view, name='credit_card'),
    url(r'^credit_card/register$', views.credit_card_register, name='credit_card_register'),
    url(r'^credit_card/remove', views.credit_card_remove, name='credit_card_remove'),
]
