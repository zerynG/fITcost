# staff/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, StackedInline
from unfold.decorators import display
from .models import UserProfile


class UserProfileInline(StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_patronymic', 'get_position', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')

    @display(description='Отчество')
    def get_patronymic(self, obj):
        try:
            return obj.profile.patronymic
        except UserProfile.DoesNotExist:
            return ''

    @display(description='Должность')
    def get_position(self, obj):
        try:
            return obj.profile.position
        except UserProfile.DoesNotExist:
            return ''


# Перерегистрируем User с кастомным админом
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'patronymic', 'position')
    search_fields = ('user__username', 'user__last_name', 'user__first_name', 'patronymic', 'position')
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Профиль', {
            'fields': ('patronymic', 'position')
        }),
    )