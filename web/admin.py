from django.contrib import admin

from .models import Event, EventGroup

admin.site.register(Event)
admin.site.register(EventGroup)
