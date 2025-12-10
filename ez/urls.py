from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_auth(request):
    return redirect('login:auth')

urlpatterns = [
    path('', redirect_to_auth),  # Перенаправление с корня на auth/
    path('admin/', admin.site.urls),
    path('', include('login.urls')),  # Включаем URLs из приложения main
    path('workspace/', include('workspace.urls')),
    path('customers/', include('customers.urls')),  # URL для приложения customers
    path('contractors/', include('contractors.urls')),  # URL для приложения customers
    path('equipment/', include('equipment.urls')),  # URL для приложения customers
    path('employees/', include('employees.urls')),  # URL для приложения customers
    path('subcontractors/', include('subcontractors.urls')),
    path('staff/', include('staff.urls')),
    path('workspace-control/', include('workspace_control.urls')),
    path('projects/', include('projects.urls')),
    path('commercial/', include('commercial_proposal.urls')),
    path('nma/', include('nmacost.urls')),
    path('itcost/', include('itcost.urls')),
]