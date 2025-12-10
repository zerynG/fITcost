from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ['inn', 'customer_type', 'name', 'full_name', 'email', 'phone', 'created_at']
    list_filter = ['customer_type', 'created_at']
    search_fields = ['inn', 'name', 'full_name', 'email', 'phone']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('inn', 'customer_type', 'name', 'full_name')
        }),
        ('Контакты', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']