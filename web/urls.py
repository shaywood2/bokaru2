from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'web'
urlpatterns = [
    # ex: /
    url(r'^$', views.index, name='index'),
    url(r'^account/$', views.account, name='account'),
    url(r'^auth/$', views.authenticate, name='auth'),
    # Authentication views
    url(r'^login/$', auth_views.login, {'template_name': 'web/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^password_change/$', auth_views.password_change,
        {'post_change_redirect': 'web:password_change_done', 'template_name': 'web/password_change.html'},
        name='password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done,
        {'template_name': 'web/password_change_complete.html'}, name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset,
        {'post_reset_redirect': 'web:password_reset_done', 'email_template_name': 'web/password_reset_email.html',
         'template_name': 'web/password_reset.html'},
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done,
        {'template_name': 'web/password_reset_done.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': 'web:password_reset_complete', 'template_name': 'web/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'web/password_reset_complete.html'},
        name='password_reset_complete'),
]
