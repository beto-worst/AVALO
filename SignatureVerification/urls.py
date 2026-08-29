from django.urls import path
from . import views

app_name = 'SignatureVerification'

urlpatterns = [
    path('', views.index, name='index'),
    path('index_htmx_form/', views.index_htmx_form, name='index_htmx_form'),
    path('delete_contract/', views.delete_contract, name='delete_contract'),
    path('verify/', views.verify, name='verify'),
    path('resend_verification/', views.resend_verification, name='resend_verification'),
    path('webhook/', views.webhook, name='webhook'),
]