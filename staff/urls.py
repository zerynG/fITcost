from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'staff'

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),

    # Redirect для URL без слеша
    path('users', RedirectView.as_view(pattern_name='staff:user_list', permanent=False)),
]