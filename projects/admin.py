from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Project, ProjectResource


class ProjectResourceInline(TabularInline):
    model = ProjectResource
    extra = 1
    fields = ('name', 'resource_type', 'service_name', 'quantity', 'cost_price', 'final_cost')
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ['name', 'customer', 'start_date', 'end_date', 'total_cost', 'cost_price', 'net_profit', 'created_by']
    list_filter = ['start_date', 'end_date', 'customer', 'created_by']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'
    inlines = [ProjectResourceInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'customer', 'description', 'technical_spec')
        }),
        ('Даты', {
            'fields': ('start_date', 'end_date')
        }),
        ('Финансы', {
            'fields': ('tax_rate', 'total_cost', 'cost_price', 'cost_with_margin', 'net_profit')
        }),
        ('Создатель', {
            'fields': ('created_by',)
        }),
    )
    
    readonly_fields = ['total_cost', 'cost_price', 'cost_with_margin', 'net_profit']


@admin.register(ProjectResource)
class ProjectResourceAdmin(ModelAdmin):
    list_display = ['name', 'project', 'resource_type', 'service_name', 'quantity', 'cost_price', 'final_cost']
    list_filter = ['resource_type', 'project']
    search_fields = ['name', 'service_name', 'project__name']
    autocomplete_fields = ['project']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'name', 'resource_type', 'service_name')
        }),
        ('Количество и стоимость', {
            'fields': ('quantity', 'cost_price', 'final_cost')
        }),
    )