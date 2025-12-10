from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import CommercialProposal, ServiceItem


class ServiceItemInline(TabularInline):
    model = ServiceItem
    extra = 1
    fields = ('name', 'hours', 'start_date', 'end_date', 'cost')
    show_change_link = True


@admin.register(CommercialProposal)
class CommercialProposalAdmin(ModelAdmin):
    list_display = ['title', 'customer', 'creation_date', 'total_cost', 'manager_name']
    list_filter = ['creation_date', 'customer']
    search_fields = ['title', 'customer__name', 'manager_name', 'manager_email']
    date_hierarchy = 'creation_date'
    inlines = [ServiceItemInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'customer', 'creation_date')
        }),
        ('Техническое задание', {
            'fields': ('technical_spec',)
        }),
        ('Финансы', {
            'fields': ('total_cost',)
        }),
        ('Руководитель', {
            'fields': ('manager_position', 'manager_name', 'manager_email')
        }),
    )
    
    readonly_fields = ['creation_date']


@admin.register(ServiceItem)
class ServiceItemAdmin(ModelAdmin):
    list_display = ['name', 'proposal', 'hours', 'start_date', 'end_date', 'cost']
    list_filter = ['proposal', 'start_date', 'end_date']
    search_fields = ['name', 'proposal__title']
    autocomplete_fields = ['proposal']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('proposal', 'name')
        }),
        ('Период и стоимость', {
            'fields': ('hours', 'start_date', 'end_date', 'cost')
        }),
    )
