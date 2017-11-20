from django.conf.urls import url

from . import views

app_name = 'event'
urlpatterns = [
    url(r'^event/create', views.create, name='create'),
    url(r'^event/(?P<event_id>\d+)$', views.view, name='view'),
    url(r'^event/join/(?P<group_id>\d+)$', views.join, name='join'),
    url(r'^event/payment/$', views.payment, name='payment')
]
