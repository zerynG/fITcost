from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Workspace, WorkspaceMember


class WorkspaceMemberInline(TabularInline):
    model = WorkspaceMember
    extra = 1
    fields = ('user', 'permission', 'joined_at')
    readonly_fields = ['joined_at']
    show_change_link = True


@admin.register(Workspace)
class WorkspaceAdmin(ModelAdmin):
    list_display = ['name', 'subdomain', 'admin', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'subdomain', 'admin__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WorkspaceMemberInline]
    list_editable = ['is_active']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'subdomain', 'admin', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(ModelAdmin):
    list_display = ['workspace', 'user', 'permission', 'joined_at']
    list_filter = ['permission', 'joined_at', 'workspace']
    search_fields = ['workspace__name', 'user__username', 'user__email']
    date_hierarchy = 'joined_at'
    autocomplete_fields = ['workspace', 'user']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('workspace', 'user', 'permission', 'joined_at')
        }),
    )
    
    readonly_fields = ['joined_at']