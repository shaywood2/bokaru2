from django.conf.urls import url

from . import views

app_name = 'web'
urlpatterns = [
    # ex: /
    url(r'^$', views.index, name='index'),
    url(r'^test/$', views.test, name='test'),
    url(r'^search/$', views.search, name='search'),
    url(r'^results/$', views.results, name='results'),
    url(r'^event/(?P<event_id>\d+)$', views.event_view, name='event_view'),
    url(r'^event/create', views.event_create, name='event_create'),
    url(r'^event/participants/$', views.participants, name='participants'),
    url(r'^event/joined/$', views.eventjoined, name='eventjoined'),
    url(r'^matches/$', views.matches, name='matches'),
    url(r'^myevents/$', views.myevents, name='myevents'),
    url(r'^termsofuse/$', views.termsofuse, name='termsofuse'),
    url(r'^howitworks/$', views.howitworks, name='howitworks'),
    url(r'^privacypolicy/$', views.privacypolicy, name='privacypolicy'),
]
