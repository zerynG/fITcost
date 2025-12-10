from django.urls import path
from . import views

app_name = 'commercial_proposal'

urlpatterns = [
    # Список коммерческих предложений (должен быть первым)
    path('', views.proposal_list, name='proposal_list'),  # корневой путь /commercial/
    # Маршруты с workspace_id и project_id для списка
    path('workspace/<int:workspace_id>/project/<int:project_id>/', views.proposal_list, name='proposal_list_project'),
    # Создание коммерческого предложения
    path('create/', views.create_proposal, name='create_proposal'),
    # Маршруты с workspace_id и project_id для создания
    path('workspace/<int:workspace_id>/project/<int:project_id>/create/', views.create_proposal, name='create_project'),
    # Остальные маршруты
    path('<int:pk>/', views.proposal_detail, name='proposal_detail'),
    path('<int:pk>/delete/', views.delete_proposal, name='delete_proposal'),
    path('<int:pk>/pdf/', views.download_pdf, name='download_pdf'),
    path('<int:pk>/excel/', views.download_excel, name='download_excel'),
    path('<int:pk>/word/', views.download_word, name='download_word'),
    path('debug/', views.debug_urls, name='debug_urls'),
]