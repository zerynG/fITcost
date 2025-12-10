from django.urls import path
from . import views

app_name = 'workspace_control'

urlpatterns = [
    path('', views.workspace_list, name='workspace_list'),
    path('create/', views.workspace_create, name='workspace_create'),
    path('edit/<int:pk>/', views.workspace_edit, name='workspace_edit'),
    path('delete/<int:pk>/', views.workspace_delete, name='workspace_delete'),
    path('members/<int:pk>/', views.workspace_members, name='workspace_members'),
    path('members/<int:pk>/remove/<int:member_id>/', views.remove_member, name='remove_member'),
]