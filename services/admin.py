from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'cost', 'start_date', 'end_date', 'is_indefinite', 'created_at')
    list_filter = ('project', 'is_indefinite', 'created_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

