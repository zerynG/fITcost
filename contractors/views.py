from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Contractor, Service
from .forms import ContractorForm, ServiceForm
from workspace.models import Project


@login_required
def contractors_list(request, workspace_id=None, project_id=None):
    """Список исполнителей с фильтрацией по проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Показываем исполнителей из текущего проекта + те, которые можно использовать в других проектах
        contractors = Contractor.objects.filter(
            Q(project=project) | Q(can_be_shared=True, project__workspace=project.workspace)
        ).distinct()
    else:
        contractors = Contractor.objects.all()
    
    context = {
        'contractors': contractors,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'contractors/contractors_list.html', context)


@login_required
def contractor_detail(request, pk, workspace_id=None, project_id=None):
    contractor = get_object_or_404(Contractor, pk=pk)
    services = contractor.services.all()

    if request.method == 'POST':
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            service = service_form.save(commit=False)
            service.contractor = contractor
            service.save()
            if project_id and workspace_id:
                return redirect('contractors:contractor_detail_project', workspace_id=workspace_id, project_id=project_id, pk=contractor.pk)
            return redirect('contractors:contractor_detail', pk=contractor.pk)  # добавил пространство имен
    else:
        service_form = ServiceForm()

    return render(request, 'contractors/contractor_detail.html', {
        'contractor': contractor,
        'services': services,
        'service_form': service_form,
        'project_id': project_id,
        'workspace_id': workspace_id,
    })


@login_required
def contractor_create(request, workspace_id=None, project_id=None):
    """Создание исполнителя с привязкой к проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = None
    
    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            contractor = form.save(commit=False)
            if project_id:
                contractor.project = project
            contractor.save()
            messages.success(request, 'Исполнитель успешно создан')
            if project_id:
                return redirect('contractors:contractors_list_project', workspace_id=workspace_id, project_id=project_id)
            else:
                return redirect('contractors:contractors_list')
    else:
        form = ContractorForm()
        if project_id:
            form.initial['project'] = project

    context = {
        'form': form,
        'project_id': project_id,
        'workspace_id': workspace_id,
        'project': project,
    }
    return render(request, 'contractors/contractor_form.html', context)


@login_required
def contractor_edit(request, pk, workspace_id=None, project_id=None):
    contractor = get_object_or_404(Contractor, pk=pk)

    if request.method == 'POST':
        form = ContractorForm(request.POST, instance=contractor)
        if form.is_valid():
            form.save()
            if project_id and workspace_id:
                return redirect('contractors:contractors_list_project', workspace_id=workspace_id, project_id=project_id)
            return redirect('contractors:contractors_list')
    else:
        form = ContractorForm(instance=contractor)

    context = {
        'form': form,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'contractors/contractor_form.html', context)


@login_required
def contractor_delete(request, pk, workspace_id=None, project_id=None):
    contractor = get_object_or_404(Contractor, pk=pk)

    if request.method == 'POST':
        contractor.delete()
        if project_id and workspace_id:
            return redirect('contractors:contractors_list_project', workspace_id=workspace_id, project_id=project_id)
        return redirect('contractors:contractors_list')

    context = {
        'contractor': contractor,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'contractors/contractor_confirm_delete.html', context)