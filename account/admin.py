from django.contrib import admin

from .models import Account, Money

admin.site.register(Account)
admin.site.register(Money)
