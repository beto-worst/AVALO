from django.contrib import admin
from . import  models
# Register your models here.


@admin.register(models.LugarNacimientoCURP)
class AdminLugarNacimientoCURP(admin.ModelAdmin):
    ordering = ['clave']


@admin.register(models.Paises)
class AdminPaises(admin.ModelAdmin):
    pass


@admin.register(models.Estados)
class AdminEstados(admin.ModelAdmin):
    raw_id_fields = ['pais']


@admin.register(models.Municipios)
class AdminMunicipios(admin.ModelAdmin):
    raw_id_fields = ['estado']


@admin.register(models.Colonia)
class AdminColonias(admin.ModelAdmin):
    raw_id_fields = ['municipio']


@admin.register(models.Bancos)
class AdminBancos(admin.ModelAdmin):
    pass

@admin.register(models.EstadosCiviles)
class AdminEstadosCiviles(admin.ModelAdmin):
    pass

@admin.register(models.TipoINE)
class AdminTipoINE(admin.ModelAdmin):
    ordering =['tipo']

@admin.register(models.TipInmobiliario)
class adminTipInmobiliario(admin.ModelAdmin):
    ordering =['creado_en']


@admin.register(models.Folios)
class AdminFolios(admin.ModelAdmin):
    ordering=['creado_en']