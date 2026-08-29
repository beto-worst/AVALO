from django.contrib import admin
from .models import Inmueble,TipoInmueble, FotosInmuebles
# Register your models here.


@admin.register(TipoInmueble)
class AdminTipoInmueble(admin.ModelAdmin):
    pass

@admin.register(Inmueble)
class AdminInmueble(admin.ModelAdmin):
    raw_id_fields = ['tipo_inmueble','duenio','uso']


@admin.register(FotosInmuebles)
class AdminFotosInmueble(admin.ModelAdmin):
    raw_id_fields = ['inmueble_id']