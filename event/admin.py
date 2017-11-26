from django.contrib import admin
from django.contrib.gis.db import models
from django.forms.widgets import Textarea

from .models import Event, EventGroup, EventParticipant, Pick


# Change PointField types to use text area instead of a map
class DirectGeoAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.PointField: {'widget': Textarea}
    }


admin.site.register(Event, DirectGeoAdmin)
admin.site.register(EventGroup)
admin.site.register(EventParticipant)
admin.site.register(Pick)
