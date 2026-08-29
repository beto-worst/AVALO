from django.contrib import admin
from . models import CoordinateTemplates


# Register your models here.
@admin.register(CoordinateTemplates)
class CoordinateTemplatesAdmin(admin.ModelAdmin):
    list_display = ('template_name', 'doc_format', 'date_created', 'date_modified')
    list_filter = ('template_name', 'doc_format', 'date_created', 'date_modified')
    # search_fields = ('doc_format', 'template_name', 'date_created', 'date_modified')