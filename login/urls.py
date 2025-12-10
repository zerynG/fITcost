
from django.urls import path
from . import views

app_name = 'login'  # Пространство имен для приложения

urlpatterns = [
    path('auth/', views.login_view, name='auth'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
]