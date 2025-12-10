from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Список проектов
    # URL: /projects/
    path('', views.project_list, name='project_list'),
    
    # Создание нового проекта
    # URL: /projects/create/
    path('create/', views.project_create, name='project_create'),
    
    # Просмотр проекта (только чтение)
    # URL: /projects/<id>/
    path('<int:pk>/', views.project_detail, name='project_detail'),
    
    # Редактирование проекта
    # URL: /projects/<id>/edit/
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
    
    # Удаление проекта
    # URL: /projects/<id>/delete/
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Управление ресурсами проекта
    # URL: /projects/<id>/resources/
    path('<int:project_pk>/resources/', views.manage_resources, name='manage_resources'),
    
    # Добавление ресурса в проект
    # URL: /projects/<project_id>/add-resource/
    path('<int:project_pk>/add-resource/', views.add_resource, name='add_resource'),
    
    # Редактирование ресурса
    # URL: /projects/resource/<resource_id>/edit/
    path('resource/<int:resource_pk>/edit/', views.edit_resource, name='edit_resource'),
    
    # Удаление ресурса
    # URL: /projects/resource/<resource_id>/delete/
    path('resource/<int:resource_pk>/delete/', views.delete_resource, name='delete_resource'),
    
    # API: Получение услуг исполнителя
    # URL: /projects/api/contractor/<contractor_id>/services/
    path('api/contractor/<int:contractor_id>/services/', views.get_services_for_contractor, name='get_services_for_contractor'),
    
    # API: Получение данных ресурса из реестра
    # URL: /projects/api/resource/<resource_type>/<resource_id>/
    path('api/resource/<str:resource_type>/<int:resource_id>/', views.get_resource_data, name='get_resource_data'),
]