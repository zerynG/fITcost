from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Equipment

@admin.register(Equipment)
class EquipmentAdmin(ModelAdmin):
    list_display = ['name', 'acquisition_type', 'unit', 'service_cost_per_unit', 'operational_cost', 'is_active', 'created_at']
    list_filter = ['acquisition_type', 'unit', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'acquisition_type', 'is_active')
        }),
        ('Параметры', {
            'fields': ('unit', 'service_cost_per_unit', 'operational_cost')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']