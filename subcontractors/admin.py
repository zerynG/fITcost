from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Subcontractor

@admin.register(Subcontractor)
class SubcontractorAdmin(ModelAdmin):
    list_display = ['name', 'contractor_type', 'inn', 'kpp', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['contractor_type', 'is_active', 'created_at']
    search_fields = ['name', 'inn', 'kpp', 'ogrn', 'director_name', 'email', 'phone']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'contractor_type', 'is_active')
        }),
        ('Реквизиты', {
            'fields': ('inn', 'kpp', 'ogrn')
        }),
        ('Адреса', {
            'fields': ('legal_address', 'actual_address')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'director_name')
        }),
        ('Банковские реквизиты', {
            'fields': ('bank_name', 'bank_account', 'corr_account', 'bik')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )