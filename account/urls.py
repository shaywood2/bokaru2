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
    url(r'^preferences', views.preferences, name='preferences'),
    url(r'^closeaccount', views.closeaccount, name='closeaccount'),
    url(r'^history', views.history, name='history'),
    url(r'^settings$', views.settings, name='settings'),
    url(r'^close$', views.close, name='close'),
    url(r'^credit_card$', views.credit_card_view, name='credit_card'),
    url(r'^credit_card/edit$', views.credit_card_edit, name='credit_card_edit'),
    url(r'^event/pay/(?P<group_id>\d+)$', views.event_pay, name='event_pay'),
    url(r'^credit_card/register$', views.credit_card_register, name='credit_card_register'),
    url(r'^credit_card/register_pay/(?P<group_id>\d+)$', views.credit_card_register_and_pay, name='credit_card_register_and_pay'),
    url(r'^credit_card/remove', views.credit_card_remove, name='credit_card_remove'),
]
