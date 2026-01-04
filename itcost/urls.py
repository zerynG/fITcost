from django.urls import path

from . import views

app_name = "itcost"

urlpatterns = [
    path("", views.CostDashboardView.as_view(), name="dashboard"),
    path("workspace/<int:workspace_id>/project/<int:project_id>/", views.CostDashboardView.as_view(), name="dashboard_project"),
    path(
        "calculations/new/",
        views.CostCalculationCreateView.as_view(),
        name="calculation_create",
    ),
    path(
        "workspace/<int:workspace_id>/project/<int:project_id>/calculations/new/",
        views.CostCalculationCreateView.as_view(),
        name="calculation_create_project",
    ),
    path(
        "calculations/<int:pk>/",
        views.CostCalculationDetailView.as_view(),
        name="calculation_detail",
    ),
    path(
        "workspace/<int:workspace_id>/project/<int:project_id>/calculations/<int:pk>/",
        views.CostCalculationDetailView.as_view(),
        name="calculation_detail_project",
    ),
    path(
        "calculations/<int:pk>/edit/",
        views.CostCalculationUpdateView.as_view(),
        name="calculation_edit",
    ),
    path(
        "workspace/<int:workspace_id>/project/<int:project_id>/calculations/<int:pk>/edit/",
        views.CostCalculationUpdateView.as_view(),
        name="calculation_edit_project",
    ),
    path(
        "calculations/<int:pk>/delete/",
        views.CostCalculationDeleteView.as_view(),
        name="calculation_delete",
    ),
    path(
        "workspace/<int:workspace_id>/project/<int:project_id>/calculations/<int:pk>/delete/",
        views.CostCalculationDeleteView.as_view(),
        name="calculation_delete_project",
    ),
    path("settings/", views.OrganizationSettingsUpdateView.as_view(), name="settings"),
    path("workspace/<int:workspace_id>/project/<int:project_id>/settings/", views.OrganizationSettingsUpdateView.as_view(), name="settings_project"),
    path("roles/", views.RoleAssignmentView.as_view(), name="roles"),
    path("workspace/<int:workspace_id>/project/<int:project_id>/roles/", views.RoleAssignmentView.as_view(), name="roles_project"),
]

