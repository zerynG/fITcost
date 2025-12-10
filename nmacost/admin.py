from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import NMACost, ResourceItem


class ResourceItemInline(TabularInline):
    model = ResourceItem
    extra = 1
    fields = ('name', 'description', 'quantity', 'unit', 'unit_cost', 'total_cost')
    readonly_fields = ['total_cost']
    show_change_link = True


@admin.register(NMACost)
class NMACostAdmin(ModelAdmin):
    list_display = ['get_project_name', 'development_period', 'total_cost', 'created_at']
    list_filter = ['created_at', 'development_period']
    search_fields = ['project__name', 'development_period']
    date_hierarchy = 'created_at'
    readonly_fields = ['total_cost', 'created_at', 'updated_at']
    inlines = [ResourceItemInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'development_period')
        }),
        ('Финансовая информация', {
            'fields': ('total_cost',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_project_name(self, obj):
        return obj.project.name if obj.project else "Без проекта"
    get_project_name.short_description = 'Проект'


@admin.register(ResourceItem)
class ResourceItemAdmin(ModelAdmin):
    list_display = ['name', 'nmacost', 'quantity', 'unit', 'unit_cost', 'total_cost_display']
    list_filter = ['unit', 'nmacost']
    search_fields = ['name', 'description', 'nmacost__project__name']
    readonly_fields = ['total_cost']
    autocomplete_fields = ['nmacost']

    @display(description='Общая стоимость', ordering='total_cost')
    def total_cost_display(self, obj):
        return f"{obj.total_cost} руб."
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('nmacost', 'name', 'description')
        }),
        ('Количество и стоимость', {
            'fields': ('quantity', 'unit', 'unit_cost', 'total_cost')
        }),
    )