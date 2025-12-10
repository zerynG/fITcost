from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ['full_name_display', 'position', 'salary', 'tax_rate', 'is_active', 'created_at']
    list_filter = ['position', 'tax_rate', 'is_active', 'created_at']
    search_fields = ['last_name', 'first_name', 'middle_name', 'position', 'email']
    list_editable = ['is_active']
    ordering = ['last_name', 'first_name']
    date_hierarchy = 'created_at'
    
    @display(description='ФИО', ordering='last_name')
    def full_name_display(self, obj):
        parts = [obj.last_name, obj.first_name]
        if obj.middle_name:
            parts.append(obj.middle_name)
        return ' '.join(parts)
    
    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'email', 'phone')
        }),
        ('Работа', {
            'fields': ('position', 'salary', 'tax_rate', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']