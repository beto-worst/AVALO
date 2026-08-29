from django.contrib import admin
from .models import TiposDocumento, FormatosDocumento, Archivos
# Register your models here.


@admin.register(TiposDocumento)
class TiposDocumentoAdmin(admin.ModelAdmin):
    pass


@admin.register(FormatosDocumento)
class FormatosDocumentoAdmin(admin.ModelAdmin):
    raw_id_fields = ['tipo']
    
@admin.register(Archivos)
class ArchivosAdmin(admin.ModelAdmin):
    raw_id_fields = ['tipo']
    
    