from django.urls import path
from . import views

app_name = 'nmacost'

urlpatterns = [
    # Список НМА (должен быть первым)
    path('', views.nmacost_list, name='nmacost-list'),
    # Маршруты с workspace_id и project_id для списка НМА проекта
    path('workspace/<int:workspace_id>/project/<int:project_id>/', views.nmacost_list, name='nmacost-list-project'),
    # Создание НМА
    path('create/', views.nmacost_create, name='nmacost-create'),
    # Маршруты с workspace_id и project_id для создания
    path('workspace/<int:workspace_id>/project/<int:project_id>/create/', views.nmacost_create, name='create_project'),
    # Остальные маршруты
    path('<int:nmacost_id>/', views.nmacost_detail, name='nmacost-detail'),
    path('<int:nmacost_id>/edit/', views.nmacost_edit, name='nmacost-edit'),
    path('<int:nmacost_id>/delete/', views.nmacost_delete, name='nmacost-delete'),
    path('<int:nmacost_id>/resource/add/', views.resource_add, name='resource-add'),
    path('<int:nmacost_id>/resource/<int:resource_id>/delete/', views.resource_delete, name='resource-delete'),
    path('<int:nmacost_id>/export/pdf/', views.export_pdf, name='export-pdf'),
    path('<int:nmacost_id>/export/excel/', views.export_excel, name='export-excel'),
    path('<int:nmacost_id>/export/word/', views.export_word, name='export-word'),
    # Маршруты с workspace_id и project_id для редактирования и удаления
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:nmacost_id>/edit/', views.nmacost_edit, name='nmacost-edit-project'),
    path('workspace/<int:workspace_id>/project/<int:project_id>/<int:nmacost_id>/delete/', views.nmacost_delete, name='nmacost-delete-project'),
]