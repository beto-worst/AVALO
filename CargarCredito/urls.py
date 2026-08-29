from django.urls import path
from . import views

app_name = 'CargarCredito'

urlpatterns = [
    path('', views.index, name='index'),
    path('delete_customer/', views.delete_customer, name='delete_customer'),
    path('payment_successful/', views.payment_successful, name='payment_successful'),
    path('product_select/', views.product_select, name='product_select'),
    path('payment_canceled/', views.payment_canceled, name='payment_canceled'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
]