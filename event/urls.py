from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'event'
urlpatterns = [
    url(r'^create/$', login_required(views.CreateEventWizard.as_view()), name='create'),
    url(r'^(?P<event_id>\d+)$', views.view, name='view'),
    url(r'^join/(?P<group_id>\d+)$', views.join, name='join'),
    url(r'^join_confirmation/$', views.join_confirmation, name='join_confirmation'),
    url(r'^leave/(?P<event_id>\d+)$', views.leave, name='leave'),
    url(r'^leave_confirmation/$', views.leave_confirmation, name='leave_confirmation')
]
