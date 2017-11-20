from django.conf.urls import url

from . import views

app_name = 'event'
urlpatterns = [
    url(r'^event/(?P<event_id>\d+)$', views.event_view, name='event_view'),
    url(r'^event/create', views.event_create, name='event_create'),
    url(r'^event/join/(?P<group_id>\d+)$', views.event_join, name='event_join'),
    url(r'^event/payment/$', views.payment, name='payment')
]
