from django.urls import path
from .views import MunicipiosList, MunicipiosAdd, MunicipiosEdit, MunicipiosDelete, EstadosList, EstadosEdit
from .views import EstadosAdd, EstadosDelete, apiTipoINE, apiLugarNacimiento

app_name ='Generales'
urlpatterns = [
    path('Municipios', MunicipiosList.as_view(), name='MunicipiosList'),
    path('Municipios/add', MunicipiosAdd.as_view(), name='MunicipiosAdd'),
    path('Municipios/edit/<int:pk>', MunicipiosEdit.as_view(), name='MunicipiosEdit'),
    path('Municipios/delete/<int:pk>', MunicipiosDelete.as_view(), name='MunicipiosDelete'),
    path('Estados', EstadosList.as_view(), name='EstadosList'),
    path('Estados/edit/<int:pk>', EstadosEdit.as_view(), name='EstadosEdit'),
    path('Estados/add', EstadosAdd.as_view(), name='EstadosAdd'),
    path('Estados/delete/<int:pk>', EstadosDelete.as_view(), name='EstadosDelete'),
    path('apiTipoINE', apiTipoINE,name='API Tipo INE'),
    path('apiLugarNacimiento', apiLugarNacimiento,name='API Lugar Nacimiento')
    #path('', views.index, name='index'), entidad,dia,mes,nombre,apellido1,apellido2,anio,sexo
]