from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Service
from .forms import ServiceForm
from workspace.models import Project


@login_required
def service_list(request, workspace_id=None, project_id=None):
    """Список услуг с фильтрацией по проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Показываем услуги только для текущего проекта
        services = Service.objects.filter(project=project)
    else:
        services = Service.objects.all()
    
    context = {
        'services': services,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'services/service_list.html', context)


@login_required
def service_create(request, workspace_id=None, project_id=None):
    """Создание услуги с привязкой к проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = None
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            if project_id:
                service.project = project
            service.save()
            messages.success(request, 'Услуга успешно создана')
            if project_id and workspace_id:
                return redirect('services:service_list_project', workspace_id=workspace_id, project_id=project_id)
            else:
                return redirect('services:service_list')
    else:
        form = ServiceForm()
        if project_id:
            form.fields['project'].initial = project

    context = {
        'form': form,
        'project_id': project_id,
        'workspace_id': workspace_id,
        'project': project,
    }
    return render(request, 'services/service_form.html', context)


@login_required
def service_detail(request, pk, workspace_id=None, project_id=None):
    """Просмотр услуги"""
    service = get_object_or_404(Service, pk=pk)
    # Если project_id не передан, пытаемся получить из service
    if not project_id and service.project:
        project_id = service.project.id
        if service.project.workspace:
            workspace_id = service.project.workspace.id

    context = {
        'service': service,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'services/service_detail.html', context)


@login_required
def service_edit(request, pk, workspace_id=None, project_id=None):
    """Редактирование услуги"""
    service = get_object_or_404(Service, pk=pk)
    # Если project_id не передан, пытаемся получить из service
    if not project_id and service.project:
        project_id = service.project.id
        if service.project.workspace:
            workspace_id = service.project.workspace.id

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Услуга успешно обновлена')
            if project_id and workspace_id:
                return redirect('services:service_list_project', workspace_id=workspace_id, project_id=project_id)
            else:
                return redirect('services:service_list')
    else:
        form = ServiceForm(instance=service)

    context = {
        'form': form,
        'service': service,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'services/service_form.html', context)


@login_required
def service_delete(request, pk, workspace_id=None, project_id=None):
    """Удаление услуги"""
    service = get_object_or_404(Service, pk=pk)
    # Если project_id не передан, пытаемся получить из service
    if not project_id and service.project:
        project_id = service.project.id
        if service.project.workspace:
            workspace_id = service.project.workspace.id

    if request.method == 'POST':
        service_name = service.name
        service.delete()
        messages.success(request, f'Услуга "{service_name}" успешно удалена')
        if project_id and workspace_id:
            return redirect('services:service_list_project', workspace_id=workspace_id, project_id=project_id)
        else:
            return redirect('services:service_list')

    context = {
        'service': service,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'services/service_confirm_delete.html', context)

