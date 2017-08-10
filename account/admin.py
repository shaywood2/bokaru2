from django.contrib import admin

from .models import Account, UserPreference

admin.site.register(Account)
admin.site.register(UserPreference)
