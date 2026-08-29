from django.contrib import admin
from .models import Products, UserPayment, UserPaymentHistory

# Register your models here.
@admin.register(Products)
class CargarCreditoProductsAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'description', 'price', 'stripe_price_id', 'status', 'date_created', 'date_updated')
    list_filter = ('name', 'description', 'price', 'stripe_price_id', 'status', 'date_created', 'date_updated')


@admin.register(UserPayment)
class UserPaymentAdmin(admin.ModelAdmin):
    pass