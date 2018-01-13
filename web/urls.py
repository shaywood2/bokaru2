from django.conf.urls import url

from . import views

app_name = 'web'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^search/(?P<place_name>\w+)/$', views.search_by_place, name='search_by_place'),
    url(r'^my_events/$', views.my_events, name='my_events'),
    url(r'^my_matches/$', views.my_matches, name='my_matches'),
    url(r'^terms_of_service/$', views.terms_of_service, name='terms_of_service'),
    url(r'^how_it_works/$', views.how_it_works, name='how_it_works'),
    url(r'^privacy_statement/$', views.privacy_statement, name='privacy_statement'),
    url(r'^refund_policy/$', views.refund_policy, name='refund_policy'),
    url(r'^about_us/$', views.about_us, name='about_us')
]
