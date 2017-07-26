from django.conf.urls import url

from . import views

app_name = 'chat'
urlpatterns = [
    # ex: /chat/session
    url(r'^session/$', views.session_create, name='session'),
    # ex: /chat/token/12345/
    url(r'^token/(?P<session_id>.+)/$', views.token_create, name='token'),
    # ex: /chat/dates/event/22/
    url(r'^event_dates/(?P<event_id>.+)/$', views.get_user_dates, name='get_user_dates'),
    # ex: /chat/upcoming_event/
    url(r'^upcoming_event/$', views.get_upcoming_event, name='get_upcoming_event'),
    # ex: /chat/upcoming_event/
    url(r'^current_date/(?P<event_id>.+)/$', views.get_current_date, name='get_current_date'),
    # ex: /chat/
    url(r'^$', views.live_event, name='live_event'),
]
