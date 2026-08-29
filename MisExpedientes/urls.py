from django.urls import path
from django.urls import path, re_path
from . import views

app_name = 'MisExpedientes'

urlpatterns = [
    path("", views.index, name="index"),
    path("", views.index, kwargs={'cliente_id': None}, name="index"),
    path('getByID/<int:persona>',views.getInfoAPI, name='get API Expedienites'),
    path('getCategoriaByID/<int:categoria>',views.getCategoriaByID, name='get API Expedienites'),
    path('getCategorias',views.getCategorias, name='get API Expedienites'),
    path("<int:cliente_id>/", views.index, name="index"),
    path("<int:cliente_id>/<str:page>", views.index, name="index"),
    path("<int:cliente_id>/<str:page>/<int:err>", views.index, name="index"),
    re_path(r'^up_load/$', views.up_load, name='up_load'),
    path('up_load/', views.up_load, name='up_load'),
    path('delete_document/', views.delete_document, name='delete_document'),
    path('delete_document/<cliente_id>/<doc_id>/<page>', views.delete_document, name='delete_document'),
    ]