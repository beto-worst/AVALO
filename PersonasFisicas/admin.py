from django.contrib import admin
from .models import PersonaFisica
# Register your models here.


@admin.register(PersonaFisica)
class PersonaFisicaAdmin(admin.ModelAdmin):
    pass