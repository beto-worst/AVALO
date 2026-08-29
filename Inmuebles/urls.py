from django.urls import path
from .views import index as indexview, imagenes_inmuebles, add
app_name = 'Inmuebles'

urlpatterns = [
    path('', indexview, name='Inmuebles Index'),
    path('add', add, name='Inmuebles add'),
    path('inmueblesfotos', imagenes_inmuebles, name='Inmuebles fotos api')
]