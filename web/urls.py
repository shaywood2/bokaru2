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
    url(r'^event/joined/$', views.event_joined, name='event_joined'),
    url(r'^event/payment/$', views.payment, name='payment'),
    url(r'^event/join/(?P<group_id>\d+)$', views.event_join, name='event_join'),
    url(r'^matches/$', views.matches, name='matches'),
    url(r'^lobby/$', views.lobby, name='lobby'),
    url(r'^match/$', views.match, name='match'),
    url(r'^live/$', views.live, name='live'),
    url(r'^myevents/$', views.myevents, name='myevents'),
    url(r'^termsofuse/$', views.termsofuse, name='termsofuse'),
    url(r'^howitworks/$', views.howitworks, name='howitworks'),
    url(r'^privacypolicy/$', views.privacypolicy, name='privacypolicy'),
]
