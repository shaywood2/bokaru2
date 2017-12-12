from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from account.forms import RegistrationForm
from account.views import RegistrationView

urlpatterns = [
    url(r'^', include('web.urls')),
    url(r'^', include('account.urls')),
    url(r'^event/', include('event.urls')),
    url(r'^chat/', include('chat.urls')),
    url(r'^admin/', admin.site.urls),
    # Registration and authentication views
    url(r'^register/$',
        RegistrationView.as_view(
            form_class=RegistrationForm
        ),
        name='auth_register',
        ),
    url(r'^', include('registration.backends.hmac.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
