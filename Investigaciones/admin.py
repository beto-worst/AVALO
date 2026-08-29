from django.contrib import admin
from .models import Investigacion, InvestigacionPremium, Referencias

# Register your models here.
@admin.register(Investigacion)
class InvestigacionAdmin(admin.ModelAdmin):
    raw_id_fields = ['investigado']
    

@admin.register(InvestigacionPremium)
class InvestigacionPremium(admin.ModelAdmin):
    pass


@admin.register(Referencias)
class ReferenciasAdmin(admin.ModelAdmin):
    pass