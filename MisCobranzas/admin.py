from django.contrib import admin
from .models import CobranzasMessages, CobranzasPlantillas


@admin.register(CobranzasPlantillas)
class CobranzasPlantillasAdmin(admin.ModelAdmin):
    list_display = ('Broker', 'Notification', 'Frequency', 'name_subject', 'status', 'created', 'updated')
    list_filter = ('Broker', 'Notification', 'Frequency', 'status', 'created', 'updated')
    # search_fields = ('Broker', 'Notification', 'Frequency', 'status', 'created', 'updated')


# Register your models here.
@admin.register(CobranzasMessages)
class CobranzasMessagesAdmin(admin.ModelAdmin):
    list_display = ('Broker', 'Client', 'Notification', 'Frequency', 'status', 'delivered', 'created', 'updated')
    list_filter = ('Broker', 'Client', 'Notification', 'Frequency', 'status', 'delivered', 'created', 'updated')
    # search_fields = ('Broker', 'Client', 'Notification', 'Frequency', 'status', 'delivered', 'created', 'updated')
