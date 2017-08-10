from django.contrib import admin

from .models import Event, EventGroup, EventParticipant, Pick, Memo

admin.site.register(Event)
admin.site.register(EventGroup)
admin.site.register(EventParticipant)
admin.site.register(Pick)
admin.site.register(Memo)
