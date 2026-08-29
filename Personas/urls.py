from django.urls import path
from . import views

app_name = 'Personas'

urlpatterns = [
     path('PersonasPF', views.PersonaFList.as_view(), name='Personas Fisicas Index'),
     path('PersonasPF/edit/<int:pk>', views.PersonasEdit.as_view(), name='PF Edit'),
     path('PersonasPF/delete/<int:pk>', views.PersonasDelete.as_view(), name='PF Delete'),
     path('PersonasPF/add', views.PersonasAdd.as_view(), name='PF Add'),
     path('getByID/<int:id>', views.getByIDJSON, name='API JSON'),
]