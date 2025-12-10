from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Contractor, Service


class ServiceInline(TabularInline):
    model = Service
    extra = 1
    fields = ('name', 'unit', 'rate')
    show_change_link = True


@admin.register(Contractor)
class ContractorAdmin(ModelAdmin):
    list_display = ['full_name_display', 'contract_type', 'tax_rate', 'default_unit', 'default_rate']
    list_filter = ['contract_type', 'tax_rate', 'default_unit']
    search_fields = ['last_name', 'first_name', 'middle_name']
    inlines = [ServiceInline]
    
    @display(description='ФИО', ordering='last_name')
    def full_name_display(self, obj):
        parts = [obj.last_name, obj.first_name]
        if obj.middle_name:
            parts.append(obj.middle_name)
        return ' '.join(parts)
    
    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name')
        }),
        ('Договор', {
            'fields': ('contract_type', 'tax_rate')
        }),
        ('Параметры по умолчанию', {
            'fields': ('default_unit', 'default_rate'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ['name', 'contractor', 'unit', 'rate']
    list_filter = ['unit', 'contractor']
    search_fields = ['name', 'contractor__last_name', 'contractor__first_name']
    autocomplete_fields = ['contractor']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('contractor', 'name')
        }),
        ('Параметры', {
            'fields': ('unit', 'rate')
        }),
    )