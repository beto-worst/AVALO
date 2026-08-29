from django.contrib import admin
from .models import CustomUser, ConfiguracionUsuariosLB
from django.contrib.auth.models import User
# Register your models here.

@admin.register(CustomUser)
class AdminCustomUser(admin.ModelAdmin):
    raw_id_fields = ['usuario']

@admin.register(ConfiguracionUsuariosLB)
class AdminConfigUsuariosLB(admin.ModelAdmin):
     raw_id_fields = ['usuario']
     verbose_name='Configuración Limite Usuarios'
     verbose_name_plural='Configuración Limite Usuarios'
