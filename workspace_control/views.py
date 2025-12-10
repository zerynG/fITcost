from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Workspace, WorkspaceMember
from .forms import WorkspaceForm, WorkspaceMemberForm


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def workspace_list(request):
    workspaces = Workspace.objects.all()
    return render(request, 'workspace_control/workspace_list.html', {'workspaces': workspaces})


@login_required
@user_passes_test(is_admin)
def workspace_create(request):
    if request.method == 'POST':
        form = WorkspaceForm(request.POST)
        if form.is_valid():
            workspace = form.save()
            WorkspaceMember.objects.create(
                workspace=workspace,
                user=workspace.admin,
                permission='admin'
            )
            messages.success(request, 'Рабочая область успешно создана!')
            return redirect('workspace_control:workspace_list')
    else:
        form = WorkspaceForm()

    return render(request, 'workspace_control/workspace_form.html', {'form': form, 'title': 'Создание рабочей области'})


@login_required
@user_passes_test(is_admin)
def workspace_edit(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)

    if request.method == 'POST':
        form = WorkspaceForm(request.POST, instance=workspace)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рабочая область успешно обновлена!')
            return redirect('workspace_control:workspace_list')
    else:
        form = WorkspaceForm(instance=workspace)

    return render(request, 'workspace_control/workspace_form.html',
                  {'form': form, 'title': 'Редактирование рабочей области'})


@login_required
@user_passes_test(is_admin)
def workspace_delete(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)

    if request.method == 'POST':
        try:
            workspace_name = workspace.name
            workspace.delete()
            messages.success(request, f'Рабочая область "{workspace_name}" успешно удалена!')
            return redirect('workspace_control:workspace_list')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении рабочей области: {str(e)}')
            return redirect('workspace_control:workspace_list')

    return render(request, 'workspace_control/workspace_confirm_delete.html', {'workspace': workspace})


@login_required
@user_passes_test(is_admin)
def workspace_members(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)
    members = workspace.control_members.all()

    if request.method == 'POST':
        form = WorkspaceMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.workspace = workspace
            member.save()
            messages.success(request, 'Пользователь добавлен в рабочую область!')
            return redirect('workspace_control:workspace_members', pk=pk)
    else:
        form = WorkspaceMemberForm()

    return render(request, 'workspace_control/workspace_members.html', {
        'workspace': workspace,
        'members': members,
        'form': form
    })


@login_required
@user_passes_test(is_admin)
def remove_member(request, pk, member_id):
    member = get_object_or_404(WorkspaceMember, pk=member_id, workspace_id=pk)

    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Пользователь удален из рабочей области!')

    return redirect('workspace_control:workspace_members', pk=pk)