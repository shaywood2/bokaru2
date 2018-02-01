from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
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
        # Authentication views
        path('', include('django.contrib.auth.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
