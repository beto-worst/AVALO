from django.urls import path
from .views import SustentoList as index
from .views import SustentoCreate, SustentoEdit, SustentoDelete
from .views import UsodesueloList, UsosueloDelete, UsosueloCreate, UsosueloEdit

app_name = 'Normativas'

urlpatterns = [
     path('SustentoLegal', index.as_view(), name='SustentoLegal Index'),
     path('SustentoLegal/add', SustentoCreate.as_view(), name='SustentoLegal Add'),
     path('SustentoLegal/edit/<int:pk>', SustentoEdit.as_view(), name='SustentoLegal Edit'),
     path('SustentoLegal/delete/<int:pk>', SustentoDelete.as_view(), name='SustentoLegal Delete'),
     path('Usodesuelo', UsodesueloList.as_view(), name='Uso de suelo Index'),
     path('Usodesuelo/delete/<int:pk>', UsosueloDelete.as_view(), name='UsoSuelo Delete'),
     path('Usodesuelo/add', UsosueloCreate.as_view(), name='UsoSuelo Add'),
     path('Usodesuelo/edit/<int:pk>', UsosueloEdit.as_view(), name='UsoSuelo Edit'),
]
