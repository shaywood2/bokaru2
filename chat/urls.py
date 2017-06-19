from django.conf.urls import url

from . import views

app_name = 'chat'
urlpatterns = [
    # ex: /chat/session
    url(r'^session/$', views.session_create, name='session'),
    # ex: /chat/token/12345
    url(r'^token/(?P<session_id>.+)/$', views.token_create, name='token'),
]
