# staff/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_list(request):
    users = User.objects.all().order_by('last_name', 'first_name')
    return render(request, 'staff/user_list.html', {'users': users})


@login_required
@permission_required('auth.add_user', raise_exception=True)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Пользователь {user.get_full_name()} успешно создан!')
            return redirect('staff:user_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'staff/user_form.html', {
        'form': form,
        'title': 'Создание пользователя'
    })


@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Данные пользователя {user.get_full_name()} успешно обновлены!')
            return redirect('staff:user_list')
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, 'staff/user_form.html', {
        'form': form,
        'title': 'Редактирование пользователя',
        'user': user
    })


@login_required
@permission_required('auth.delete_user', raise_exception=True)
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        full_name = user.get_full_name()
        user.delete()
        messages.success(request, f'Пользователь {full_name} успешно удален!')
        return redirect('staff:user_list')

    return render(request, 'staff/user_confirm_delete.html', {'user': user})