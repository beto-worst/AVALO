from django.urls import path
from . import views

app_name='Investigaciones'
urlpatterns = [

    path('20e355df03730ba3d1a98c7f95673a3c', views.webhook_receiver, name='index'),
]