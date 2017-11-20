from django.conf.urls import url

from . import views

app_name = 'web'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^terms_of_use/$', views.terms_of_use, name='terms_of_use'),
    url(r'^how_it_works/$', views.how_it_works, name='how_it_works'),
    url(r'^privacy_policy/$', views.privacy_policy, name='privacy_policy')
]
