from django.contrib import admin
from .models import TicketStatus, TicketCategory, Ticket, TicketComment, TicketSubCategory


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 1


class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketCommentInline]
    list_display = ('title', 'creator', 'assignee', 'category', 'status', 'priority', 'created_at', 'updated_at')
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description']
    fieldsets = [
        (None, {'fields': ['title', 'creator', 'assignee', 'category', 'status', 'priority', 'description']}),
        # ('Date information', {'fields': ['updated_at'], 'classes': ['collapse']}),
    ]


# Register your models here.
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketStatus)
admin.site.register(TicketCategory)
admin.site.register(TicketSubCategory)
# admin.site.register(TicketComment)
