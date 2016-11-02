from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^', include('web.urls')),
    url(r'^profile/', include('account.urls')),
    url(r'^chat/', include('chat.urls')),
    url(r'^admin/', admin.site.urls),
]
