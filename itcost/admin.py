from django.contrib import admin

from .models import CostCalculation, OrganizationSettings, RoleAssignment


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    list_display = ("company_name", "director_full_name", "contact_email", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(CostCalculation)
class CostCalculationAdmin(admin.ModelAdmin):
    list_display = (
        "project_name",
        "client_name",
        "development_cost",
        "intangible_asset_cost",
        "commercial_offer_cost",
        "created_by",
        "created_at",
    )
    list_filter = ("created_at", "created_by")
    search_fields = ("project_name", "client_name")
    readonly_fields = (
        "development_cost",
        "intangible_asset_cost",
        "commercial_offer_cost",
        "created_at",
        "updated_at",
    )


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    list_filter = ("role", "assigned_at")
    search_fields = ("user__username", "user__email")

