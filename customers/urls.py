from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # Старые маршруты для обратной совместимости
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    # Маршруты с workspace_id и project_id
    path('workspace/<int:workspace_id>/project/<int:project_id>/', views.customer_list, name='customer_list_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/create/', views.customer_create, name='customer_create_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit_project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete_project'),
]