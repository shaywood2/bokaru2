from django.conf.urls import url

from . import views

app_name = 'chat'
urlpatterns = [
    url(r'^$', views.live_event, name='live_event'),
    # ex: /chat/pick/target_user/123/event/456/response/1/
    # Responses are: 1 - Yes, 0 - No and 2 - Maybe
    url(r'^pick/target_user/(?P<target_user_id>.+)/event/(?P<event_id>.+)/response/(?P<response>.+)/$',
        views.create_pick, name='create_pick'),
    url(r'^test/(?P<user1>\d+)/(?P<user2>\d+)/$', views.live_event_test),
    url(r'^gen/(?P<event_id>\d+)/$', views.generate),
    url(r'^dates/(?P<event_id>\d+)/$', views.get_dates)
]
