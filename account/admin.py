from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.sessions.models import Session
from django.contrib.gis.db import models
from django.forms.widgets import Textarea

from .models import Account, UserPreference


# Register session objects in admin console
class SessionAdmin(ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ['session_key', '_session_data', 'expire_date']


# Change PointField types to use text area instead of a map
class DirectGeoAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.PointField: {'widget': Textarea}
    }


admin.site.register(Account, DirectGeoAdmin)
admin.site.register(UserPreference)
admin.site.register(Session, SessionAdmin)
