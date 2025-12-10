from django.urls import path
from . import views

app_name = 'employees'  # это создает пространство имен

urlpatterns = [
    # Старые маршруты для обратной совместимости
    path('', views.employee_list, name='employee_list'),
    path('create/', views.employee_create, name='employee_create'),
    # Маршруты с workspace_id и project_id
    path('workspace/<int:workspace_id>/project/<int:project_id>/', views.employee_list, name='employee_list_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/create/', views.employee_create, name='employee_create_project'),
    # Остальные маршруты
    path('edit/<int:pk>/', views.employee_edit, name='employee_edit'),
    path('delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('toggle-active/<int:pk>/', views.employee_toggle_active, name='employee_toggle_active'),
    # Маршруты с workspace_id и project_id для редактирования и удаления
    path('workspace/<int:workspace_id>/project/<int:project_id>/edit/<int:pk>/', views.employee_edit, name='employee_edit_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/delete/<int:pk>/', views.employee_delete, name='employee_delete_project'),
]