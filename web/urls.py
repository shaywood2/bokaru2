from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'web'
urlpatterns = [
    # ex: /
    url(r'^$', views.index, name='index'),
    url(r'^account/$', views.account, name='account'),
    url(r'^login/$', auth_views.login, {'template_name': 'web/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
]
