from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q
from .models import Employee
from .forms import EmployeeForm, EmployeeFilterForm
from workspace.models import Project


@login_required
def employee_list(request, workspace_id=None, project_id=None):
    """Список сотрудников с фильтрацией по проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Показываем сотрудников из текущего проекта + те, которые можно использовать в других проектах
        employees = Employee.objects.filter(
            Q(project=project) | Q(can_be_shared=True, project__workspace=project.workspace)
        ).distinct()
    else:
        employees = Employee.objects.all()
    
    filter_form = EmployeeFilterForm(request.GET or None)

    if filter_form.is_valid():
        position = filter_form.cleaned_data.get('position')
        active_only = filter_form.cleaned_data.get('active_only')

        if position:
            employees = employees.filter(position__icontains=position)
        if active_only:
            employees = employees.filter(is_active=True)

    context = {
        'employees': employees,
        'filter_form': filter_form,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_create(request, workspace_id=None, project_id=None):
    """Создание нового сотрудника с привязкой к проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = None
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            if project_id:
                employee.project = project
            employee.save()
            messages.success(request, f'Сотрудник {employee.get_full_name()} успешно добавлен!')
            if project_id:
                return redirect('employees:employee_list_project', workspace_id=workspace_id, project_id=project_id)
            else:
                return redirect('employees:employee_list')
    else:
        form = EmployeeForm()
        if project_id:
            form.initial['project'] = project

    context = {
        'form': form,
        'title': 'Добавить сотрудника',
        'project_id': project_id,
        'workspace_id': workspace_id,
        'project': project,
    }
    return render(request, 'employees/employee_form.html', context)


def employee_edit(request, pk, workspace_id=None, project_id=None):
    """Редактирование сотрудника"""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Данные сотрудника {employee.get_full_name()} обновлены!')
            if project_id and workspace_id:
                return redirect('employees:employee_list_project', workspace_id=workspace_id, project_id=project_id)
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form, 
        'title': 'Редактировать сотрудника', 
        'employee': employee,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'employees/employee_form.html', context)


def employee_delete(request, pk, workspace_id=None, project_id=None):
    """Удаление сотрудника"""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        employee_name = employee.get_full_name()
        employee.delete()
        messages.success(request, f'Сотрудник {employee_name} удален!')
        if project_id and workspace_id:
            return redirect('employees:employee_list_project', workspace_id=workspace_id, project_id=project_id)
        return redirect('employees:employee_list')

    context = {
        'employee': employee,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'employees/employee_confirm_delete.html', context)


def employee_toggle_active(request, pk):
    """Активация/деактивация сотрудника"""
    if request.method != 'POST':
        messages.error(request, 'Неверный метод запроса')
        return redirect('employees:employee_list')
    
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = not employee.is_active
    employee.save()

    action = "активирован" if employee.is_active else "деактивирован"
    messages.success(request, f'Сотрудник {employee.get_full_name()} {action}!')

    # Получаем workspace_id и project_id из POST параметров или GET параметров
    workspace_id = request.POST.get('workspace_id') or request.GET.get('workspace_id')
    project_id = request.POST.get('project_id') or request.GET.get('project_id')
    
    # Если не передан, пытаемся получить из объекта employee
    if not project_id and employee.project:
        project_id = employee.project.id
        if employee.project.workspace:
            workspace_id = employee.project.workspace.id
    
    # Редирект на правильную страницу в зависимости от наличия project_id и workspace_id
    if project_id and workspace_id:
        return redirect('employees:employee_list_project', workspace_id=workspace_id, project_id=project_id)
    return redirect('employees:employee_list')


def calculate_employee_cost(request):
    """Расчет стоимости работы сотрудника (API endpoint)"""
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        working_days = request.POST.get('working_days')

        try:
            employee = Employee.objects.get(pk=employee_id, is_active=True)
            working_days = int(working_days)

            # Упрощенный расчет
            daily_cost = employee.calculate_daily_rate(working_days)
            total_cost = daily_cost * working_days

            return JsonResponse({
                'success': True,
                'daily_cost': round(daily_cost, 2),
                'total_cost': round(total_cost, 2),
                'employee_name': employee.get_full_name()
            })

        except (Employee.DoesNotExist, ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid parameters'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})