from django.urls import path
from . import views

app_name = 'subcontractors'

urlpatterns = [
    # Старые маршруты для обратной совместимости
    path('', views.subcontractor_list, name='list'),
    path('create/', views.subcontractor_create, name='create'),
    # Маршруты с workspace_id и project_id
    path('workspace/<int:workspace_id>/project/<int:project_id>/', views.subcontractor_list, name='list_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/create/', views.subcontractor_create, name='create_project'),
    # Остальные маршруты
    path('<int:pk>/edit/', views.subcontractor_edit, name='edit'),
    path('<int:pk>/delete/', views.subcontractor_delete, name='delete'),
    path('<int:pk>/toggle-active/', views.subcontractor_toggle_active, name='toggle_active'),
    path('<int:pk>/', views.subcontractor_detail, name='detail'),
    # Маршруты с workspace_id и project_id для просмотра, редактирования и удаления
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/', views.subcontractor_detail, name='detail_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/edit/', views.subcontractor_edit, name='edit_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/delete/', views.subcontractor_delete, name='delete_project'),
]