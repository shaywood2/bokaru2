from django.conf.urls import url, include
from django.contrib import admin
from account.views import RegistrationView
from account.forms import RegistrationForm

urlpatterns = [
    url(r'^', include('web.urls')),
    url(r'^profile/', include('account.urls')),
    url(r'^chat/', include('chat.urls')),
    url(r'^admin/', admin.site.urls),
    # Registration and authentication views
    url(r'^account/register/$',
        RegistrationView.as_view(
            form_class=RegistrationForm
        ),
        name='registration_register',
        ),
    url(r'^account/', include('registration.backends.hmac.urls')),
]
