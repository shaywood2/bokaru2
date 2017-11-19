from django.conf.urls import url
from . import views

app_name = 'account'
urlpatterns = [
    url(r'^profile$', views.view, name='view'),
    url(r'^profile/view/(?P<username>\w+)$', views.view_user, name='view_user'),
    url(r'^profile/edit$', views.edit, name='edit'),
    url(r'^profile/edit/photo$', views.update_photo, name='update_photo'),
    url(r'^account$', views.preferences, name='preferences'),
    url(r'^account/payment$', views.preferences_payment, name='payment'),
    url(r'^account/close$', views.close, name='close'),
    # url(r'^account/payment/edit$', views.credit_card_edit, name='credit_card_edit'),
    # url(r'^event/pay/(?P<group_id>\d+)$', views.event_pay, name='event_pay'),
    # url(r'^credit_card/register$', views.credit_card_register, name='credit_card_register'),
    # url(r'^credit_card/register_pay/(?P<group_id>\d+)$', views.credit_card_register_and_pay, name='credit_card_register_and_pay'),
    # url(r'^credit_card/remove', views.credit_card_remove, name='credit_card_remove'),
]
