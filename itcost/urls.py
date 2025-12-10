from django.urls import path

from . import views

app_name = "itcost"

urlpatterns = [
    path("", views.CostDashboardView.as_view(), name="dashboard"),
    path(
        "calculations/new/",
        views.CostCalculationCreateView.as_view(),
        name="calculation_create",
    ),
    path(
        "calculations/<int:pk>/",
        views.CostCalculationDetailView.as_view(),
        name="calculation_detail",
    ),
    path(
        "calculations/<int:pk>/edit/",
        views.CostCalculationUpdateView.as_view(),
        name="calculation_edit",
    ),
    path(
        "calculations/<int:pk>/delete/",
        views.CostCalculationDeleteView.as_view(),
        name="calculation_delete",
    ),
    path("settings/", views.OrganizationSettingsUpdateView.as_view(), name="settings"),
    path("roles/", views.RoleAssignmentView.as_view(), name="roles"),
]

