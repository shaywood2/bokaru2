from django.contrib import admin

from .models import UserPaymentInfo, Product
from .model_transaction import Transaction

admin.site.register(UserPaymentInfo)
admin.site.register(Product)
admin.site.register(Transaction)
