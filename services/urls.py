from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Старые маршруты для обратной совместимости
    path('', views.service_list, name='service_list'),
    path('create/', views.service_create, name='service_create'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('<int:pk>/delete/', views.service_delete, name='service_delete'),
    # Маршруты с workspace_id и project_id
    path('workspace/<int:workspace_id>/project/<int:project_id>/', views.service_list, name='service_list_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/create/', views.service_create, name='service_create_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/', views.service_detail, name='service_detail_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/edit/', views.service_edit, name='service_edit_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/delete/', views.service_delete, name='service_delete_project'),
]

