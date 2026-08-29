from django.contrib import admin
from .models import reponses
# Register your models here.

@admin.register(reponses)
class responsesAdmin(admin.ModelAdmin):
    pass