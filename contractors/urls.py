from django.urls import path
from . import views

app_name = 'contractors'

urlpatterns = [
    # Старые маршруты для обратной совместимости
    path('', views.contractors_list, name='contractors_list'),
    path('new/', views.contractor_create, name='contractor_create'),
    # Маршруты с workspace_id и project_id
    path('workspace/<int:workspace_id>/project/<int:project_id>/', views.contractors_list, name='contractors_list_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/create/', views.contractor_create, name='contractor_create_project'),
    # Остальные маршруты
    path('<int:pk>/', views.contractor_detail, name='contractor_detail'),
    path('<int:pk>/edit/', views.contractor_edit, name='contractor_edit'),
    path('<int:pk>/delete/', views.contractor_delete, name='contractor_delete'),
    # Маршруты с workspace_id и project_id для редактирования и удаления
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/edit/', views.contractor_edit, name='contractor_edit_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/delete/', views.contractor_delete, name='contractor_delete_project'),
]