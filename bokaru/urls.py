from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from account.forms import RegistrationForm
from account.views import RegistrationView
from . import views

urlpatterns = \
    [
        path('', include('web.urls')),
        path('', include('account.urls')),
        path('event/', include('event.urls')),
        path('chat/', include('chat.urls')),
        path('admin/', admin.site.urls),
        path('script/activate_events/', views.activate_events),
        path('script/process_payments/', views.process_payments),
        # Registration and authentication views
        path('register/',
             RegistrationView.as_view(
                 form_class=RegistrationForm
             ),
             name='auth_register',
             ),
        path('', include('registration.backends.hmac.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
