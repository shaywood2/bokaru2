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
    url(r'^account/payment_history$', views.preferences_payment_history, name='payment_history'),
    url(r'^account/close$', views.close, name='close'),
    # Usage example: $.post( "/memo/about/2/", "lorem ipsum dolor sit amet");
    url(r'^memo/about/(?P<about_user_id>\d+)/$', views.create_or_update_memo, name='memo')
]
