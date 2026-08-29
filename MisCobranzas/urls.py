from django.urls import path
from . import views

app_name = 'MisCobranzas'

urlpatterns = [
    path('', views.index, name='index'),
    path('update_status/<int:pk>/<str:scheduled_status>', views.update_status, name='update_status'),
    path('delete_message/<int:pk>', views.delete_message, name='delete_message'),
    path('tsc/', views.status_callback, name='tsc'),
]