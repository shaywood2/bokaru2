from django.contrib import admin

from .models import Account, UserPreferences

admin.site.register(Account)
admin.site.register(UserPreferences)
