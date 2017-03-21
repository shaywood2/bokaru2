from django.contrib import admin

from .models import Account, Payment

admin.site.register(Account)
admin.site.register(Payment)
