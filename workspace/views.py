from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Workspace, Project, WorkspaceMember
from .forms import ProjectForm, WorkspaceMemberForm, WorkspaceForm


@login_required
def workspace_list(request):
    """Список всех рабочих областей, доступных пользователю"""
    # Показываем только активные рабочие области, в которых пользователь является участником или администратором
    workspaces = Workspace.objects.filter(
        is_active=True,
        members__user=request.user
    ).distinct()
    
    return render(request, 'workspace/workspace_list.html', {'workspaces': workspaces})


@login_required
def workspace_create(request):
    """Создание новой рабочей области"""
    if request.method == 'POST':
        form = WorkspaceForm(request.POST)
        if form.is_valid():
            workspace = form.save(commit=False)
            workspace.save()
            # Автоматически добавляем администратора как владельца
            WorkspaceMember.objects.create(
                workspace=workspace,
                user=workspace.admin,
                role='owner'
            )
            messages.success(request, 'Рабочая область успешно создана!')
            return redirect('workspace:workspace_list')
    else:
        form = WorkspaceForm()
        # По умолчанию устанавливаем текущего пользователя как администратора
        form.fields['admin'].initial = request.user

    return render(request, 'workspace/workspace_form.html', {'form': form, 'title': 'Создание рабочей области'})


@login_required
def workspace_enter(request, workspace_id):
    """Вход в рабочую область - перенаправление на дашборд"""
    workspace = get_object_or_404(Workspace, id=workspace_id, is_active=True)
    
    # Проверка доступа пользователя к workspace
    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user).exists():
        messages.error(request, "У вас нет доступа к этой рабочей области")
        return redirect('workspace:workspace_list')
    
    return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)


@login_required
def workspace_dashboard(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id, is_active=True)

    # Проверка доступа пользователя к workspace
    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user).exists():
        messages.error(request, "У вас нет доступа к этой рабочей области")
        return redirect('workspace:workspace_list')

    projects = workspace.projects.all()
    members = workspace.members.all()
    
    # Проверяем, является ли пользователь владельцем или администратором
    user_member = WorkspaceMember.objects.filter(workspace=workspace, user=request.user).first()
    is_admin = user_member and user_member.role in ['owner', 'admin']

    context = {
        'workspace': workspace,
        'projects': projects,
        'members': members,
        'is_admin': is_admin,
        'workspace_id': workspace_id,
        'project_id': None,  # На дашборде рабочей области нет активного проекта
    }
    return render(request, 'workspace/dashboard.html', context)


@login_required
def project_create(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user, role__in=['owner', 'admin']).exists():
        messages.error(request, "У вас нет прав для создания проектов")
        return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.workspace = workspace
            project.save()
            messages.success(request, "Проект успешно создан")
            return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'workspace': workspace,
        'title': 'Создание проекта',
        'workspace_id': workspace_id,
        'project_id': None,
    }
    return render(request, 'workspace/project_form.html', context)


@login_required
def project_edit(request, workspace_id, project_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)
    project = get_object_or_404(Project, id=project_id, workspace=workspace)

    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user, role__in=['owner', 'admin']).exists():
        messages.error(request, "У вас нет прав для редактирования проектов")
        return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Проект успешно обновлен")
            return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'workspace': workspace,
        'project': project,
        'title': 'Редактирование проекта',
        'workspace_id': workspace_id,
        'project_id': project_id,
    }
    return render(request, 'workspace/project_form.html', context)


@login_required
def project_delete(request, workspace_id, project_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)
    project = get_object_or_404(Project, id=project_id, workspace=workspace)

    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user, role__in=['owner', 'admin']).exists():
        messages.error(request, "У вас нет прав для удаления проектов")
        return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)

    if request.method == 'POST':
        project.delete()
        messages.success(request, "Проект успешно удален")
        return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)

    context = {
        'workspace': workspace,
        'project': project,
        'workspace_id': workspace_id,
        'project_id': project_id,
    }
    return render(request, 'workspace/project_confirm_delete.html', context)


@login_required
def project_detail(request, workspace_id, project_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)
    project = get_object_or_404(Project, id=project_id, workspace=workspace)

    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user).exists():
        messages.error(request, "У вас нет доступа к этому проекту")
        return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)

    # Обновляем стоимость проекта перед отображением
    project.calculate_costs()
    # Перезагружаем проект из БД чтобы получить обновленные значения
    project.refresh_from_db()

    context = {
        'workspace': workspace,
        'project': project,
        'workspace_id': workspace_id,
        'project_id': project_id,
    }
    return render(request, 'workspace/project_detail.html', context)


@login_required
def manage_members(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user, role__in=['owner', 'admin']).exists():
        messages.error(request, "У вас нет прав для управления участниками")
        return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)

    members = workspace.members.all()

    if request.method == 'POST':
        form = WorkspaceMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.workspace = workspace
            member.save()
            messages.success(request, "Участник успешно добавлен")
            return redirect('workspace:manage_members', workspace_id=workspace_id)
    else:
        form = WorkspaceMemberForm()

    context = {
        'workspace': workspace,
        'members': members,
        'form': form,
        'workspace_id': workspace_id,
        'project_id': None,
    }
    return render(request, 'workspace/manage_members.html', context)


@login_required
def remove_member(request, workspace_id, member_id):
    workspace = get_object_or_404(Workspace, id=workspace_id, is_active=True)

    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user, role__in=['owner', 'admin']).exists():
        messages.error(request, "У вас нет прав для управления участниками")
        return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)

    member = get_object_or_404(WorkspaceMember, id=member_id, workspace=workspace)

    if request.method == 'POST':
        member.delete()
        messages.success(request, "Участник успешно удален")

    return redirect('workspace:manage_members', workspace_id=workspace_id)


@login_required
def workspace_delete(request, workspace_id):
    """Удаление рабочей области (soft delete)"""
    workspace = get_object_or_404(Workspace, id=workspace_id, is_active=True)
    
    # Проверка прав - владелец или глобальный администратор может удалить рабочую область
    user_member = WorkspaceMember.objects.filter(workspace=workspace, user=request.user).first()
    is_owner = user_member and user_member.role == 'owner'
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_superuser):
        messages.error(request, "Только владелец или администратор может удалить рабочую область")
        return redirect('workspace:workspace_dashboard', workspace_id=workspace_id)

    if request.method == 'POST':
        workspace.delete()  # Используем наш метод delete (soft delete)
        messages.success(request, f'Рабочая область "{workspace.name}" успешно удалена!')
        return redirect('workspace:workspace_list')

    context = {
        'workspace': workspace,
        'workspace_id': workspace_id,
        'project_id': None,
    }
    return render(request, 'workspace/workspace_confirm_delete.html', context)