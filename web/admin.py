from django.contrib import admin

from .models import Event, EventGroup, EventParticipant

admin.site.register(Event)
admin.site.register(EventGroup)
admin.site.register(EventParticipant)
