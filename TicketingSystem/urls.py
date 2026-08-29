from django.urls import path
from . import views

app_name = 'TicketingSystem'

urlpatterns = [
    path('', views.index, name='index'),
    path('index_htmx/', views.index_htmx, name='index_htmx'),
    path('ticket/<int:ticket_id>', views.ticket_by_id, name='ticket_by_id'),
    path('ticket_admin/', views.ticket_admin, name='ticket_admin'),
    path('ticket_admin_edit/', views.ticket_admin_edit, name='ticket_admin_edit'),
    path('ticket_admin_edit/<int:ticket_id>', views.ticket_admin_edit, name='ticket_admin_edit'),
]