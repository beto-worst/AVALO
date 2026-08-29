from django.contrib import admin
from .models import SustentoLegal, Usodesuelo
# Register your models here.

@admin.register(SustentoLegal)
class SustentoLegalAdmin(admin.ModelAdmin):
    pass


@admin.register(Usodesuelo)
class UsodesueloAdmin(admin.ModelAdmin):
    pass
