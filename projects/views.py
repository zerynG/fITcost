from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Project, ProjectResource
from workspace.models import Project as WorkspaceProject, ProjectResource as WorkspaceProjectResource
from .forms import ProjectForm, ProjectResourceForm
from employees.forms import EmployeeForm
from contractors.forms import ContractorForm, ServiceForm
from subcontractors.forms import SubcontractorForm
from equipment.forms import EquipmentForm

@login_required
def project_list(request):
    from workspace.models import WorkspaceMember
    
    # Получаем проекты, где пользователь либо создатель, либо имеет доступ через workspace
    projects_created = Project.objects.filter(created_by=request.user)
    
    # Получаем workspace пользователя
    user_workspaces = WorkspaceMember.objects.filter(user=request.user).values_list('workspace', flat=True)
    projects_from_workspace = Project.objects.filter(workspace__in=user_workspaces)
    
    # Объединяем и удаляем дубликаты
    projects = (projects_created | projects_from_workspace).distinct()
    
    context = {
        'projects': projects,
        'today': timezone.now().date()  # Теперь timezone определен
    }
    return render(request, 'projects/project_list.html', context)

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Проект успешно создан!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})


@login_required
def project_detail(request, pk):
    """Просмотр проекта (только чтение)"""
    from workspace.models import WorkspaceMember
    
    # Ищем проект сначала в workspace, затем в старом projects
    try:
        project = WorkspaceProject.objects.get(pk=pk)
    except WorkspaceProject.DoesNotExist:
        # Если не найден в workspace, пробуем найти в старом projects
        project = get_object_or_404(Project, pk=pk)
    
    # Проверка доступа: либо проект создан пользователем, либо пользователь имеет доступ к workspace проекта
    has_access = False
    if hasattr(project, 'created_by') and project.created_by == request.user:
        has_access = True
    elif hasattr(project, 'workspace') and project.workspace:
        has_access = WorkspaceMember.objects.filter(
            workspace=project.workspace,
            user=request.user
        ).exists()
    
    if not has_access:
        from django.contrib import messages
        messages.error(request, "У вас нет доступа к этому проекту")
        return redirect('projects:project_list')
    
    resources = project.projectresource_set.all()
    
    # Получаем workspace_id и project_id для сайдбара
    workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else None
    project_id = project.id

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'resources': resources,
        'read_only': True,
        'workspace_id': workspace_id,
        'project_id': project_id,
    })


@login_required
def project_edit(request, pk):
    """Редактирование проекта"""
    from workspace.models import WorkspaceMember
    
    # Ищем проект сначала в workspace, затем в старом projects
    try:
        project = WorkspaceProject.objects.get(pk=pk)
    except WorkspaceProject.DoesNotExist:
        project = get_object_or_404(Project, pk=pk)
    
    # Проверка доступа: либо проект создан пользователем, либо пользователь является admin/owner workspace
    has_access = False
    if hasattr(project, 'created_by') and project.created_by == request.user:
        has_access = True
    elif hasattr(project, 'workspace') and project.workspace:
        has_access = WorkspaceMember.objects.filter(
            workspace=project.workspace,
            user=request.user,
            role__in=['owner', 'admin']
        ).exists()
    
    if not has_access:
        messages.error(request, "У вас нет прав для редактирования этого проекта")
        return redirect('projects:project_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            project.calculate_costs()
            messages.success(request, 'Проект успешно обновлен!')
            # Получаем workspace_id и project_id для редиректа
            workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else None
            project_id = project.id
            if workspace_id and project_id:
                return redirect('projects:manage_resources', workspace_id=workspace_id, project_id=project_id)
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    # Получаем workspace_id и project_id для сайдбара
    workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else None
    project_id = project.id

    return render(request, 'projects/project_edit.html', {
        'project': project,
        'form': form,
        'workspace_id': workspace_id,
        'project_id': project_id,
    })


@login_required
def manage_resources(request, workspace_id=None, project_id=None, project_pk=None):
    """Управление ресурсами проекта - отдельная страница"""
    from workspace.models import WorkspaceMember, Workspace
    
    # Определяем project_id (новая структура имеет приоритет)
    if project_id is not None:
        project_pk = project_id
    
    # Ищем проект сначала в workspace, затем в старом projects
    try:
        project = WorkspaceProject.objects.get(pk=project_pk)
    except WorkspaceProject.DoesNotExist:
        # Если не найден в workspace, пробуем найти в старом projects
        project = get_object_or_404(Project, pk=project_pk)
    
    # Проверка workspace_id (если передан в URL, должен совпадать с проектом)
    if workspace_id is not None:
        if hasattr(project, 'workspace') and project.workspace:
            if project.workspace.id != workspace_id:
                messages.error(request, "Неверный workspace для проекта")
                return redirect('projects:project_list')
        else:
            messages.error(request, "Проект не принадлежит workspace")
            return redirect('projects:project_list')
    
    # Проверка доступа: либо проект создан пользователем, либо пользователь имеет доступ к workspace проекта
    has_access = False
    if hasattr(project, 'created_by') and project.created_by == request.user:
        has_access = True
    elif hasattr(project, 'workspace') and project.workspace:
        has_access = WorkspaceMember.objects.filter(
            workspace=project.workspace,
            user=request.user
        ).exists()
    
    if not has_access:
        messages.error(request, "У вас нет доступа к этому проекту")
        return redirect('projects:project_list')
    
    # Получаем workspace_id и project_id для сайдбара
    workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else workspace_id
    project_id = project.id
    
    # Обработка POST запроса для добавления ресурса
    if request.method == 'POST':
        from decimal import Decimal
        from datetime import datetime as dt
        
        resource_type = request.POST.get('resource_type')
        resource_id = request.POST.get('resource_id')
        service_name = request.POST.get('service_name', '')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        quantity = request.POST.get('quantity', '1')
        margin = request.POST.get('margin', '0')
        subcontractor_rate = request.POST.get('subcontractor_rate')
        service_id = request.POST.get('service')
        
        if not resource_type or not resource_id:
            messages.error(request, 'Пожалуйста, выберите тип ресурса и ресурс из списка')
        elif not start_date or not end_date:
            messages.error(request, 'Пожалуйста, заполните даты начала и окончания')
        else:
            try:
                # Получаем выбранный ресурс
                employee = None
                contractor = None
                subcontractor = None
                equipment = None
                resource_name = ''
                
                if resource_type == 'employee':
                    from employees.models import Employee
                    employee = Employee.objects.get(pk=resource_id, is_active=True)
                    resource_name = employee.get_full_name()
                    if not service_name:
                        service_name = f"Услуга {employee.get_full_name()}"
                elif resource_type == 'contractor':
                    from contractors.models import Contractor
                    contractor = Contractor.objects.get(pk=resource_id)
                    resource_name = str(contractor)
                    if not service_name:
                        service_name = f"Услуга {contractor}"
                elif resource_type == 'subcontractor':
                    from subcontractors.models import Subcontractor
                    subcontractor = Subcontractor.objects.get(pk=resource_id, is_active=True)
                    resource_name = subcontractor.name
                    if not service_name:
                        service_name = f"Услуга {subcontractor.name}"
                elif resource_type == 'equipment':
                    from equipment.models import Equipment
                    equipment = Equipment.objects.get(pk=resource_id, is_active=True)
                    resource_name = equipment.name
                    if not service_name:
                        service_name = f"Услуга {equipment.name}"
                
                # Получаем услугу для исполнителя
                service = None
                if resource_type == 'contractor' and service_id:
                    from contractors.models import Service
                    try:
                        service = Service.objects.get(pk=service_id)
                    except Service.DoesNotExist:
                        pass
                
                # Преобразуем даты
                start_date_obj = dt.strptime(start_date, '%Y-%m-%d').date() if start_date else None
                end_date_obj = dt.strptime(end_date, '%Y-%m-%d').date() if end_date else None
                
                # Создаем ресурс проекта
                if isinstance(project, WorkspaceProject):
                    workspace_resource = WorkspaceProjectResource(
                        project=project,
                        name=resource_name,
                        resource_type=resource_type,
                        employee=employee,
                        contractor=contractor,
                        subcontractor=subcontractor,
                        equipment=equipment,
                        service=service,
                        service_name=service_name,
                        start_date=start_date_obj,
                        end_date=end_date_obj,
                        quantity=Decimal(quantity) if quantity else Decimal('1'),
                        margin=Decimal(margin) if margin else Decimal('0'),
                        subcontractor_rate=Decimal(subcontractor_rate) if subcontractor_rate else None,
                    )
                    workspace_resource.calculate_costs()
                    workspace_resource.save()
                else:
                    resource = ProjectResource(
                        project=project,
                        name=resource_name,
                        resource_type=resource_type,
                        employee=employee,
                        contractor=contractor,
                        subcontractor=subcontractor,
                        equipment=equipment,
                        service=service,
                        service_name=service_name,
                        start_date=start_date_obj,
                        end_date=end_date_obj,
                        quantity=Decimal(quantity) if quantity else Decimal('1'),
                        margin=Decimal(margin) if margin else Decimal('0'),
                        subcontractor_rate=Decimal(subcontractor_rate) if subcontractor_rate else None,
                    )
                    resource.calculate_costs()
                    resource.save()
                
                project.calculate_costs()
                messages.success(request, 'Ресурс успешно добавлен в проект!')
                # Редирект на эту же страницу
                if workspace_id and project_id:
                    return redirect('projects:manage_resources', workspace_id=workspace_id, project_id=project_id)
                else:
                    return redirect('projects:manage_resources_legacy', project_pk=project.pk)
            except Exception as e:
                import traceback
                messages.error(request, f'Ошибка при добавлении ресурса: {str(e)}')
    
    # Пересчитываем стоимость проекта перед отображением
    project.calculate_costs()
    # Перезагружаем проект из БД чтобы получить обновленные значения
    project.refresh_from_db()
    
    # Получаем ресурсы в зависимости от типа проекта
    if isinstance(project, WorkspaceProject):
        resources = WorkspaceProjectResource.objects.filter(project=project)
    else:
        resources = project.projectresource_set.all()
    
    # Получаем все ресурсы из реестров для выбора (ограничиваем проектом/воркспейсом)
    from employees.models import Employee
    from contractors.models import Contractor
    from subcontractors.models import Subcontractor
    from equipment.models import Equipment
    from customers.models import Customer
    
    ws = project.workspace if hasattr(project, 'workspace') and project.workspace else None

    # Получаем уже добавленные ресурсы проекта для исключения
    if isinstance(project, WorkspaceProject):
        added_employees = WorkspaceProjectResource.objects.filter(project=project, employee__isnull=False).values_list('employee_id', flat=True)
        added_contractors = WorkspaceProjectResource.objects.filter(project=project, contractor__isnull=False).values_list('contractor_id', flat=True)
        added_subcontractors = WorkspaceProjectResource.objects.filter(project=project, subcontractor__isnull=False).values_list('subcontractor_id', flat=True)
        added_equipment = WorkspaceProjectResource.objects.filter(project=project, equipment__isnull=False).values_list('equipment_id', flat=True)
    else:
        added_employees = ProjectResource.objects.filter(project=project, employee__isnull=False).values_list('employee_id', flat=True)
        added_contractors = ProjectResource.objects.filter(project=project, contractor__isnull=False).values_list('contractor_id', flat=True)
        added_subcontractors = ProjectResource.objects.filter(project=project, subcontractor__isnull=False).values_list('subcontractor_id', flat=True)
        added_equipment = ProjectResource.objects.filter(project=project, equipment__isnull=False).values_list('equipment_id', flat=True)
    
    # Ресурсы для выбора (используются в форме добавления) - исключаем уже добавленные
    available_employees = Employee.objects.filter(
        Q(project=project) | Q(can_be_shared=True, project__workspace=ws),
        is_active=True
    ).exclude(id__in=added_employees).distinct()

    available_contractors = Contractor.objects.filter(
        Q(project=project) | Q(can_be_shared=True, project__workspace=ws)
    ).exclude(id__in=added_contractors).distinct()

    available_subcontractors = Subcontractor.objects.filter(
        Q(project=project) | Q(can_be_shared=True, project__workspace=ws),
        is_active=True
    ).exclude(id__in=added_subcontractors).distinct()

    available_equipment = Equipment.objects.filter(
        Q(project=project) | Q(can_be_shared=True, project__workspace=ws),
        is_active=True
    ).exclude(id__in=added_equipment).distinct()
    
    # Получаем связанные сущности проекта
    customer = project.customer if hasattr(project, 'customer') else None
    commercial_proposal = project.commercial_proposal if hasattr(project, 'commercial_proposal') else None
    # Получаем первую НМА стоимость (если есть несколько)
    nma_cost = project.nma_cost if hasattr(project, 'nma_cost') else None

    # Подготавливаем данные для статистики
    stats = {
        'total_resources': resources.count(),
        'employees_count': resources.filter(resource_type='employee').count(),
        'contractors_count': resources.filter(resource_type='contractor').count(),
        'subcontractors_count': resources.filter(resource_type='subcontractor').count(),
        'equipment_count': resources.filter(resource_type='equipment').count(),
    }
    
    return render(request, 'projects/manage_resources.html', {
        'project': project,
        'resources': resources,
        'available_employees': available_employees,
        'available_contractors': available_contractors,
        'available_subcontractors': available_subcontractors,
        'available_equipment': available_equipment,
        'customer': customer,
        'commercial_proposal': commercial_proposal,
        'nma_cost': nma_cost,
        'stats': stats,
        'workspace_id': workspace_id,
        'project_id': project_id,
    })


@login_required
def add_resource(request, workspace_id=None, project_id=None, project_pk=None):
    from workspace.models import WorkspaceMember
    
    # Определяем project_id (новая структура имеет приоритет)
    if project_id is not None:
        project_pk = project_id
    
    # Ищем проект сначала в workspace, затем в старом projects
    try:
        project = WorkspaceProject.objects.get(pk=project_pk)
    except WorkspaceProject.DoesNotExist:
        # Если не найден в workspace, пробуем найти в старом projects
        project = get_object_or_404(Project, pk=project_pk)
    
    # Проверка workspace_id (если передан в URL, должен совпадать с проектом)
    if workspace_id is not None:
        if hasattr(project, 'workspace') and project.workspace:
            if project.workspace.id != workspace_id:
                messages.error(request, "Неверный workspace для проекта")
                return redirect('projects:project_list')
        else:
            messages.error(request, "Проект не принадлежит workspace")
            return redirect('projects:project_list')
    
    # Проверка доступа: либо проект создан пользователем, либо пользователь имеет доступ к workspace проекта
    has_access = False
    if hasattr(project, 'created_by') and project.created_by == request.user:
        has_access = True
    elif hasattr(project, 'workspace') and project.workspace:
        has_access = WorkspaceMember.objects.filter(
            workspace=project.workspace,
            user=request.user
        ).exists()
    
    if not has_access:
        messages.error(request, "У вас нет доступа к этому проекту")
        return redirect('projects:project_list')
    
    # Импортируем модели
    from employees.models import Employee
    from contractors.models import Contractor
    from subcontractors.models import Subcontractor
    from equipment.models import Equipment
    
    # Получаем все ресурсы из реестров для выпадающих списков
    employees = Employee.objects.filter(is_active=True)
    contractors = Contractor.objects.all()
    subcontractors = Subcontractor.objects.filter(is_active=True)
    equipment_list = Equipment.objects.filter(is_active=True)
    
    # Получаем workspace_id и project_id для сайдбара и ссылок
    workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else workspace_id
    project_id = project.id
    
    # Получаем режим работы: 'existing' (добавить существующий) или 'new' (создать новый)
    mode = request.GET.get('mode', 'existing')
    # Получаем тип ресурса из GET параметра (если есть)
    resource_type = request.GET.get('type', None)
    # Получаем ID выбранного ресурса из реестра (если есть)
    selected_employee_id = request.GET.get('employee_id', None)
    selected_contractor_id = request.GET.get('contractor_id', None)
    selected_subcontractor_id = request.GET.get('subcontractor_id', None)
    selected_equipment_id = request.GET.get('equipment_id', None)
    # Флаг для кнопки "Добавить еще один ресурс"
    add_another = request.GET.get('add_another', False)

    if request.method == 'POST':
        # Определяем, какой тип формы отправлен
        form_type = request.POST.get('form_type', 'resource')
        
        # Если создается новый ресурс (Employee, Contractor и т.д.)
        if form_type == 'create_resource':
            resource_type = request.POST.get('resource_type')
            created_resource = None
            
            if resource_type == 'employee':
                employee_form = EmployeeForm(request.POST, prefix='employee')
                if employee_form.is_valid():
                    created_resource = employee_form.save()
                    messages.success(request, f'Сотрудник {created_resource.get_full_name()} успешно создан!')
                    # Перенаправляем на форму добавления ресурса с созданным сотрудником
                    return redirect(f"{request.path}?mode=existing&type=employee&employee_id={created_resource.pk}")
                else:
                    context = {
                        'project': project,
                        'mode': 'new',
                        'resource_type': resource_type,
                        'employees': employees,
                        'contractors': contractors,
                        'subcontractors': subcontractors,
                        'equipment_list': equipment_list,
                        'employee_form': employee_form,
                        'contractor_form': ContractorForm(prefix='contractor'),
                        'subcontractor_form': SubcontractorForm(prefix='subcontractor'),
                        'equipment_form': EquipmentForm(prefix='equipment'),
                        'workspace_id': workspace_id,
                        'project_id': project_id,
                    }
                    return render(request, 'projects/add_resource.html', context)
            
            elif resource_type == 'contractor':
                contractor_form = ContractorForm(request.POST, prefix='contractor')
                if contractor_form.is_valid():
                    created_resource = contractor_form.save()
                    messages.success(request, f'Исполнитель {created_resource} успешно создан!')
                    return redirect(f"{request.path}?mode=existing&type=contractor&contractor_id={created_resource.pk}")
                else:
                    context = {
                        'project': project,
                        'mode': 'new',
                        'resource_type': resource_type,
                        'employees': employees,
                        'contractors': contractors,
                        'subcontractors': subcontractors,
                        'equipment_list': equipment_list,
                        'employee_form': EmployeeForm(prefix='employee'),
                        'contractor_form': contractor_form,
                        'subcontractor_form': SubcontractorForm(prefix='subcontractor'),
                        'equipment_form': EquipmentForm(prefix='equipment'),
                        'workspace_id': workspace_id,
                        'project_id': project_id,
                    }
                    return render(request, 'projects/add_resource.html', context)
            
            elif resource_type == 'subcontractor':
                subcontractor_form = SubcontractorForm(request.POST, prefix='subcontractor')
                if subcontractor_form.is_valid():
                    created_resource = subcontractor_form.save()
                    messages.success(request, f'Субподрядчик {created_resource.name} успешно создан!')
                    return redirect(f"{request.path}?mode=existing&type=subcontractor&subcontractor_id={created_resource.pk}")
                else:
                    context = {
                        'project': project,
                        'mode': 'new',
                        'resource_type': resource_type,
                        'employees': employees,
                        'contractors': contractors,
                        'subcontractors': subcontractors,
                        'equipment_list': equipment_list,
                        'employee_form': EmployeeForm(prefix='employee'),
                        'contractor_form': ContractorForm(prefix='contractor'),
                        'subcontractor_form': subcontractor_form,
                        'equipment_form': EquipmentForm(prefix='equipment'),
                        'workspace_id': workspace_id,
                        'project_id': project_id,
                    }
                    return render(request, 'projects/add_resource.html', context)
            
            elif resource_type == 'equipment':
                equipment_form = EquipmentForm(request.POST, prefix='equipment')
                if equipment_form.is_valid():
                    created_resource = equipment_form.save()
                    messages.success(request, f'Оборудование {created_resource.name} успешно создано!')
                    return redirect(f"{request.path}?mode=existing&type=equipment&equipment_id={created_resource.pk}")
                else:
                    context = {
                        'project': project,
                        'mode': 'new',
                        'resource_type': resource_type,
                        'employees': employees,
                        'contractors': contractors,
                        'subcontractors': subcontractors,
                        'equipment_list': equipment_list,
                        'employee_form': EmployeeForm(prefix='employee'),
                        'contractor_form': ContractorForm(prefix='contractor'),
                        'subcontractor_form': SubcontractorForm(prefix='subcontractor'),
                        'equipment_form': equipment_form,
                        'workspace_id': workspace_id,
                        'project_id': project_id,
                    }
                    return render(request, 'projects/add_resource.html', context)
        
        # Если создается ProjectResource
        elif form_type == 'add_resource':
            form = ProjectResourceForm(request.POST)
            if form.is_valid():
                resource = form.save(commit=False)
                resource.project = project
                
                # Автоматически заполняем название ресурса и услуги на основе выбранного ресурса
                if resource.employee:
                    if not resource.name or resource.name.strip() == '':
                        resource.name = resource.employee.get_full_name()
                    if not resource.service_name or resource.service_name.strip() == '':
                        resource.service_name = f"Услуга {resource.employee.get_full_name()}"
                elif resource.contractor:
                    if not resource.name or resource.name.strip() == '':
                        resource.name = str(resource.contractor)
                    if not resource.service_name or resource.service_name.strip() == '':
                        resource.service_name = f"Услуга {resource.contractor}"
                elif resource.subcontractor:
                    if not resource.name or resource.name.strip() == '':
                        resource.name = resource.subcontractor.name
                    if not resource.service_name or resource.service_name.strip() == '':
                        resource.service_name = f"Услуга {resource.subcontractor.name}"
                elif resource.equipment:
                    if not resource.name or resource.name.strip() == '':
                        resource.name = resource.equipment.name
                    if not resource.service_name or resource.service_name.strip() == '':
                        resource.service_name = f"Услуга {resource.equipment.name}"
                
                resource.calculate_costs()
                resource.save()
                project.calculate_costs()
                messages.success(request, 'Ресурс успешно добавлен в проект!')
                
                # Если нужно добавить еще один ресурс
                if request.POST.get('add_another') == 'on':
                    if workspace_id and project_id:
                        return redirect('projects:add_resource', workspace_id=workspace_id, project_id=project.id)
                    else:
                        return redirect('projects:add_resource', project_pk=project.pk)
                else:
                    if workspace_id and project_id:
                        return redirect('projects:manage_resources', workspace_id=workspace_id, project_id=project.id)
                    else:
                        return redirect('projects:manage_resources', project_pk=project.pk)
            else:
                # Если форма невалидна, возвращаем с ошибками
                context = {
                    'project': project,
                    'mode': mode,
                    'resource_type': resource_type,
                    'selected_employee_id': selected_employee_id,
                    'selected_contractor_id': selected_contractor_id,
                    'selected_subcontractor_id': selected_subcontractor_id,
                    'selected_equipment_id': selected_equipment_id,
                    'employees': employees,
                    'contractors': contractors,
                    'subcontractors': subcontractors,
                    'equipment_list': equipment_list,
                    'form': form,
                    'employee_form': EmployeeForm(prefix='employee'),
                    'contractor_form': ContractorForm(prefix='contractor'),
                    'subcontractor_form': SubcontractorForm(prefix='subcontractor'),
                    'equipment_form': EquipmentForm(prefix='equipment'),
                    'workspace_id': workspace_id,
                    'project_id': project_id,
                }
                return render(request, 'projects/add_resource.html', context)
    else:
        # GET запрос - подготовка формы
        initial_data = {}
        form = None
        
        # Если выбран ресурс из реестра (режим existing), предзаполняем поля ProjectResourceForm
        if mode == 'existing' and resource_type:
            if resource_type == 'employee' and selected_employee_id:
                try:
                    employee = Employee.objects.get(pk=selected_employee_id)
                    initial_data['resource_type'] = 'employee'
                    initial_data['employee'] = employee.pk
                    initial_data['name'] = employee.get_full_name()
                    initial_data['service_name'] = f"Услуга {employee.get_full_name()}"
                except Employee.DoesNotExist:
                    pass
            elif resource_type == 'contractor' and selected_contractor_id:
                try:
                    contractor = Contractor.objects.get(pk=selected_contractor_id)
                    initial_data['resource_type'] = 'contractor'
                    initial_data['contractor'] = contractor.pk
                    initial_data['name'] = str(contractor)
                    initial_data['service_name'] = f"Услуга {contractor}"
                except Contractor.DoesNotExist:
                    pass
            elif resource_type == 'subcontractor' and selected_subcontractor_id:
                try:
                    subcontractor = Subcontractor.objects.get(pk=selected_subcontractor_id)
                    initial_data['resource_type'] = 'subcontractor'
                    initial_data['subcontractor'] = subcontractor.pk
                    initial_data['name'] = subcontractor.name
                    initial_data['service_name'] = f"Услуга {subcontractor.name}"
                except Subcontractor.DoesNotExist:
                    pass
            elif resource_type == 'equipment' and selected_equipment_id:
                try:
                    equipment = Equipment.objects.get(pk=selected_equipment_id)
                    initial_data['resource_type'] = 'equipment'
                    initial_data['equipment'] = equipment.pk
                    initial_data['name'] = equipment.name
                    initial_data['service_name'] = f"Услуга {equipment.name}"
                except Equipment.DoesNotExist:
                    pass
            
            if initial_data:
                form = ProjectResourceForm(initial=initial_data)

    # Получаем workspace_id и project_id для сайдбара и ссылок
    workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else workspace_id
    project_id = project.id

    # workspace_id и project_id уже определены выше
    context = {
        'project': project,
        'mode': mode,
        'resource_type': resource_type,
        'selected_employee_id': selected_employee_id,
        'selected_contractor_id': selected_contractor_id,
        'selected_subcontractor_id': selected_subcontractor_id,
        'selected_equipment_id': selected_equipment_id,
        'employees': employees,
        'contractors': contractors,
        'subcontractors': subcontractors,
        'equipment_list': equipment_list,
        'form': form,
        'employee_form': EmployeeForm(prefix='employee'),
        'contractor_form': ContractorForm(prefix='contractor'),
        'subcontractor_form': SubcontractorForm(prefix='subcontractor'),
        'equipment_form': EquipmentForm(prefix='equipment'),
        'workspace_id': workspace_id,
        'project_id': project_id,
    }
    return render(request, 'projects/add_resource.html', context)


@login_required
def edit_resource(request, resource_pk):
    from workspace.models import WorkspaceMember
    
    # Ищем ресурс сначала в workspace, затем в старом projects
    try:
        resource = WorkspaceProjectResource.objects.get(pk=resource_pk)
    except WorkspaceProjectResource.DoesNotExist:
        resource = get_object_or_404(ProjectResource, pk=resource_pk)
    project = resource.project

    # Проверка доступа: либо проект создан пользователем, либо пользователь имеет доступ к workspace проекта
    has_access = False
    if hasattr(project, 'created_by') and project.created_by == request.user:
        has_access = True
    elif hasattr(project, 'workspace') and project.workspace:
        has_access = WorkspaceMember.objects.filter(
            workspace=project.workspace,
            user=request.user
        ).exists()
    
    if not has_access:
        messages.error(request, 'У вас нет прав для редактирования этого ресурса!')
        workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else None
        if workspace_id:
            from django.urls import reverse
            return redirect(reverse('workspace:project_detail', args=[workspace_id, project.id]))
        else:
            return redirect('projects:project_detail', pk=project.pk)

    if request.method == 'POST':
        form = ProjectResourceForm(request.POST, instance=resource)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.calculate_costs()
            resource.save()
            project.calculate_costs()
            messages.success(request, 'Ресурс успешно обновлен!')
            workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else None
            project_id = project.id
            if workspace_id and project_id:
                return redirect('projects:manage_resources', workspace_id=workspace_id, project_id=project_id)
            else:
                return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectResourceForm(instance=resource)

    # Получаем workspace_id и project_id для сайдбара и ссылок
    workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else None
    project_id = project.id

    return render(request, 'projects/edit_resource.html', {
        'project': project,
        'resource': resource,
        'form': form,
        'workspace_id': workspace_id,
        'project_id': project_id,
    })


@login_required
@require_http_methods(["GET"])
def get_services_for_contractor(request, contractor_id):
    """API endpoint для получения услуг исполнителя"""
    from contractors.models import Service
    try:
        services = Service.objects.filter(contractor_id=contractor_id)
        services_data = [{'id': s.id, 'name': s.name, 'rate': str(s.rate), 'unit': s.unit} for s in services]
        return JsonResponse({'services': services_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def get_resource_data(request, resource_type, resource_id):
    """API endpoint для получения данных ресурса из реестра"""
    try:
        if resource_type == 'employee':
            from employees.models import Employee
            resource = Employee.objects.get(pk=resource_id, is_active=True)
            return JsonResponse({
                'name': resource.get_full_name(),
                'service_name': f"Услуга {resource.get_full_name()}",
            })
        elif resource_type == 'contractor':
            from contractors.models import Contractor
            resource = Contractor.objects.get(pk=resource_id)
            return JsonResponse({
                'name': str(resource),
                'service_name': f"Услуга {resource}",
            })
        elif resource_type == 'subcontractor':
            from subcontractors.models import Subcontractor
            resource = Subcontractor.objects.get(pk=resource_id, is_active=True)
            return JsonResponse({
                'name': resource.name,
                'service_name': f"Услуга {resource.name}",
            })
        elif resource_type == 'equipment':
            from equipment.models import Equipment
            resource = Equipment.objects.get(pk=resource_id, is_active=True)
            return JsonResponse({
                'name': resource.name,
                'service_name': f"Услуга {resource.name}",
            })
        else:
            return JsonResponse({'error': 'Invalid resource type'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def get_resources_by_type(request, workspace_id, project_id, resource_type):
    """API endpoint для получения списка ресурсов по типу для проекта"""
    from workspace.models import WorkspaceMember, Project as WorkspaceProject
    
    try:
        project = WorkspaceProject.objects.get(pk=project_id, workspace_id=workspace_id)
        
        # Проверка доступа
        has_access = False
        if hasattr(project, 'created_by') and project.created_by == request.user:
            has_access = True
        elif hasattr(project, 'workspace') and project.workspace:
            has_access = WorkspaceMember.objects.filter(
                workspace=project.workspace,
                user=request.user
            ).exists()
        
        if not has_access:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        ws = project.workspace if hasattr(project, 'workspace') and project.workspace else None
        resources = []
        
        if resource_type == 'employee':
            from employees.models import Employee
            resources_qs = Employee.objects.filter(
                Q(project=project) | Q(can_be_shared=True, project__workspace=ws),
                is_active=True
            ).distinct()
            resources = [{'id': r.id, 'name': r.get_full_name(), 'type': 'employee'} for r in resources_qs]
        elif resource_type == 'contractor':
            from contractors.models import Contractor
            resources_qs = Contractor.objects.filter(
                Q(project=project) | Q(can_be_shared=True, project__workspace=ws)
            ).distinct()
            resources = [{'id': r.id, 'name': str(r), 'type': 'contractor'} for r in resources_qs]
        elif resource_type == 'subcontractor':
            from subcontractors.models import Subcontractor
            resources_qs = Subcontractor.objects.filter(
                Q(project=project) | Q(can_be_shared=True, project__workspace=ws),
                is_active=True
            ).distinct()
            resources = [{'id': r.id, 'name': r.name, 'type': 'subcontractor'} for r in resources_qs]
        elif resource_type == 'equipment':
            from equipment.models import Equipment
            resources_qs = Equipment.objects.filter(
                Q(project=project) | Q(can_be_shared=True, project__workspace=ws),
                is_active=True
            ).distinct()
            resources = [{'id': r.id, 'name': r.name, 'type': 'equipment'} for r in resources_qs]
        else:
            return JsonResponse({'error': 'Invalid resource type'}, status=400)
        
        return JsonResponse({'resources': resources})
    except WorkspaceProject.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def delete_resource(request, resource_pk):
    from workspace.models import WorkspaceMember
    
    # Ищем ресурс сначала в workspace, затем в старом projects
    try:
        resource = WorkspaceProjectResource.objects.get(pk=resource_pk)
    except WorkspaceProjectResource.DoesNotExist:
        resource = get_object_or_404(ProjectResource, pk=resource_pk)
    project = resource.project

    # Проверка доступа: либо проект создан пользователем, либо пользователь имеет доступ к workspace проекта
    has_access = False
    if hasattr(project, 'created_by') and project.created_by == request.user:
        has_access = True
    elif hasattr(project, 'workspace') and project.workspace:
        has_access = WorkspaceMember.objects.filter(
            workspace=project.workspace,
            user=request.user
        ).exists()
    
    if not has_access:
        messages.error(request, 'У вас нет прав для удаления этого ресурса!')
        workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else None
        if workspace_id:
            from django.urls import reverse
            return redirect(reverse('workspace:project_detail', args=[workspace_id, project.id]))
        else:
            return redirect('projects:project_detail', pk=project.pk)

    resource.delete()
    project.calculate_costs()
    messages.success(request, 'Ресурс успешно удален!')
    
    # Получаем workspace_id для редиректа
    workspace_id = project.workspace.id if hasattr(project, 'workspace') and project.workspace else None
    if workspace_id:
        return redirect('projects:manage_resources', workspace_id=workspace_id, project_id=project.id)
    else:
        return redirect('projects:manage_resources', project_pk=project.pk)


@login_required
def project_delete(request, pk):
    from workspace.models import WorkspaceMember
    
    # Ищем проект сначала в workspace, затем в старом projects
    try:
        project = WorkspaceProject.objects.get(pk=pk)
    except WorkspaceProject.DoesNotExist:
        project = get_object_or_404(Project, pk=pk)
    
    # Проверка доступа: либо проект создан пользователем, либо пользователь является admin/owner workspace
    has_access = False
    if hasattr(project, 'created_by') and project.created_by == request.user:
        has_access = True
    elif hasattr(project, 'workspace') and project.workspace:
        has_access = WorkspaceMember.objects.filter(
            workspace=project.workspace,
            user=request.user,
            role__in=['owner', 'admin']
        ).exists()
    
    if not has_access:
        messages.error(request, "У вас нет прав для удаления этого проекта")
        return redirect('projects:project_list')

    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Проект "{project_name}" успешно удален!')
        return redirect('projects:project_list')

    return render(request, 'projects/project_confirm_delete.html', {
        'project': project
    })