from django.contrib import admin

from .models import UserPaymentInfo, Product

admin.site.register(UserPaymentInfo)
admin.site.register(Product)
