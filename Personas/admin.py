from django.contrib import admin
from .models import Personas


@admin.register(Personas)
class PersonasAdmin(admin.ModelAdmin):
    pass