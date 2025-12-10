from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    # Старые маршруты для обратной совместимости
    path('', views.equipment_list, name='list'),
    path('create/', views.equipment_create, name='create'),
    # Маршруты с workspace_id и project_id
    path('workspace/<int:workspace_id>/project/<int:project_id>/', views.equipment_list, name='list_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/create/', views.equipment_create, name='create_project'),
    # Остальные маршруты (используем старые CBV для обратной совместимости)
    path('update/<int:pk>/', views.EquipmentUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.EquipmentDeleteView.as_view(), name='delete'),
    path('calculate/<int:equipment_id>/', views.calculate_service_cost, name='calculate'),
    # Маршруты с workspace_id и project_id для редактирования и удаления
    path('workspace/<int:workspace_id>/project/<int:project_id>/update/<int:pk>/', views.EquipmentUpdateView.as_view(), name='update_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/delete/<int:pk>/', views.EquipmentDeleteView.as_view(), name='delete_project'),
]