from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from .models import Subcontractor
from .forms import SubcontractorForm, SubcontractorFilterForm
from workspace.models import Project


@login_required
@permission_required('subcontractors.view_subcontractor', raise_exception=True)
def subcontractor_list(request, workspace_id=None, project_id=None):
    """Список субподрядчиков с фильтрацией по проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Показываем субподрядчиков из текущего проекта + тех, которых можно использовать в других проектах
        subcontractors = Subcontractor.objects.filter(
            Q(project=project) | Q(can_be_shared=True, project__workspace=project.workspace)
        ).distinct()
    else:
        subcontractors = Subcontractor.objects.all()
    
    form = SubcontractorFilterForm(request.GET)

    if form.is_valid():
        contractor_type = form.cleaned_data.get('contractor_type')
        is_active = form.cleaned_data.get('is_active')
        search = form.cleaned_data.get('search')

        if contractor_type:
            subcontractors = subcontractors.filter(contractor_type=contractor_type)

        if is_active == 'true':
            subcontractors = subcontractors.filter(is_active=True)
        elif is_active == 'false':
            subcontractors = subcontractors.filter(is_active=False)

        if search:
            subcontractors = subcontractors.filter(
                Q(name__icontains=search) |
                Q(inn__icontains=search) |
                Q(director_name__icontains=search) |
                Q(email__icontains=search)
            )

    context = {
        'subcontractors': subcontractors,
        'filter_form': form,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'subcontractors/subcontractor_list.html', context)


@login_required
@permission_required('subcontractors.add_subcontractor', raise_exception=True)
def subcontractor_create(request, workspace_id=None, project_id=None):
    """Создание субподрядчика с привязкой к проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = None
    
    if request.method == 'POST':
        form = SubcontractorForm(request.POST)
        if form.is_valid():
            subcontractor = form.save(commit=False)
            if project_id:
                subcontractor.project = project
            subcontractor.save()
            messages.success(request, f'Субподрядчик "{subcontractor.name}" успешно создан!')
            if project_id:
                return redirect('subcontractors:list_project', workspace_id=workspace_id, project_id=project_id)
            else:
                return redirect('subcontractors:list')
    else:
        form = SubcontractorForm()
        if project_id:
            form.initial['project'] = project

    context = {
        'form': form,
        'project_id': project_id,
        'workspace_id': workspace_id,
        'project': project,
    }
    return render(request, 'subcontractors/subcontractor_form.html', context)


@login_required
@permission_required('subcontractors.change_subcontractor', raise_exception=True)
def subcontractor_edit(request, pk, workspace_id=None, project_id=None):
    subcontractor = get_object_or_404(Subcontractor, pk=pk)

    if request.method == 'POST':
        form = SubcontractorForm(request.POST, instance=subcontractor)
        if form.is_valid():
            subcontractor = form.save()
            messages.success(request, f'Субподрядчик "{subcontractor.name}" успешно обновлен!')
            if project_id and workspace_id:
                return redirect('subcontractors:list_project', workspace_id=workspace_id, project_id=project_id)
            return redirect('subcontractors:list')
    else:
        form = SubcontractorForm(instance=subcontractor)

    context = {
        'form': form, 
        'subcontractor': subcontractor,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'subcontractors/subcontractor_form.html', context)


@login_required
@permission_required('subcontractors.delete_subcontractor', raise_exception=True)
def subcontractor_delete(request, pk, workspace_id=None, project_id=None):
    subcontractor = get_object_or_404(Subcontractor, pk=pk)

    if request.method == 'POST':
        name = subcontractor.name
        subcontractor.delete()
        messages.success(request, f'Субподрядчик "{name}" успешно удален!')
        if project_id and workspace_id:
            return redirect('subcontractors:list_project', workspace_id=workspace_id, project_id=project_id)
        return redirect('subcontractors:list')

    context = {
        'subcontractor': subcontractor,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'subcontractors/subcontractor_confirm_delete.html', context)


@login_required
@permission_required('subcontractors.change_subcontractor', raise_exception=True)
def subcontractor_toggle_active(request, pk):
    subcontractor = get_object_or_404(Subcontractor, pk=pk)
    subcontractor.is_active = not subcontractor.is_active
    subcontractor.save()

    status = "активен" if subcontractor.is_active else "неактивен"
    messages.success(request, f'Субподрядчик "{subcontractor.name}" теперь {status}!')

    return redirect('subcontractors:list')

@login_required
@permission_required('subcontractors.view_subcontractor', raise_exception=True)
def subcontractor_detail(request, pk, workspace_id=None, project_id=None):
    subcontractor = get_object_or_404(Subcontractor, pk=pk)
    context = {
        'subcontractor': subcontractor,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'subcontractors/subcontractor_detail.html', context)