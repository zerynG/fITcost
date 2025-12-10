from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import Equipment
from .forms import EquipmentForm
from workspace.models import Project


@login_required
def equipment_list(request, workspace_id=None, project_id=None):
    """Список оборудования с фильтрацией по проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Показываем оборудование из текущего проекта + то, которое можно использовать в других проектах
        equipment_list = Equipment.objects.filter(
            Q(project=project) | Q(can_be_shared=True, project__workspace=project.workspace)
        ).distinct().filter(is_active=True)
    else:
        equipment_list = Equipment.objects.filter(is_active=True)
    
    context = {
        'equipment_list': equipment_list,
        'active_equipment_count': equipment_list.count(),
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'equipment/equipment_list.html', context)


@login_required
def equipment_create(request, workspace_id=None, project_id=None):
    """Создание оборудования с привязкой к проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = None
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            if project_id:
                equipment.project = project
            equipment.save()
            messages.success(request, 'Оборудование успешно добавлено')
            if project_id:
                return redirect('equipment:list_project', workspace_id=workspace_id, project_id=project_id)
            else:
                return redirect('equipment:list')
    else:
        form = EquipmentForm()
        if project_id:
            form.initial['project'] = project

    context = {
        'form': form,
        'active_equipment_count': Equipment.objects.filter(is_active=True).count(),
        'project_id': project_id,
        'workspace_id': workspace_id,
        'project': project,
    }
    return render(request, 'equipment/equipment_form.html', context)


class EquipmentUpdateView(UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'equipment/equipment_form.html'
    success_url = reverse_lazy('equipment:list')

    def form_valid(self, form):
        messages.success(self.request, 'Оборудование успешно обновлено')
        equipment = form.save()
        # Проверяем, есть ли project_id в URL
        project_id = self.kwargs.get('project_id')
        workspace_id = self.kwargs.get('workspace_id')
        if project_id and workspace_id:
            return redirect('equipment:list_project', workspace_id=workspace_id, project_id=project_id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем счетчик активных инструментов в контекст
        context['active_equipment_count'] = Equipment.objects.filter(is_active=True).count()
        context['project_id'] = self.kwargs.get('project_id')
        context['workspace_id'] = self.kwargs.get('workspace_id')
        return context


class EquipmentDeleteView(DeleteView):
    model = Equipment
    template_name = 'equipment/equipment_confirm_delete.html'
    success_url = reverse_lazy('equipment:list')

    def delete(self, request, *args, **kwargs):
        equipment = self.get_object()
        equipment.is_active = False
        equipment.save()
        messages.success(request, 'Оборудование успешно удалено')
        # Проверяем, есть ли project_id в URL
        project_id = self.kwargs.get('project_id')
        workspace_id = self.kwargs.get('workspace_id')
        if project_id and workspace_id:
            return redirect('equipment:list_project', workspace_id=workspace_id, project_id=project_id)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем счетчик активных инструментов в контекст
        context['active_equipment_count'] = Equipment.objects.filter(is_active=True).count()
        context['project_id'] = self.kwargs.get('project_id')
        context['workspace_id'] = self.kwargs.get('workspace_id')
        return context


def calculate_service_cost(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    quantity = request.GET.get('quantity', 0)
    try:
        quantity = float(quantity)
        cost = equipment.calculate_service_cost(quantity)
        return JsonResponse({'cost': float(cost)})
    except ValueError:
        return JsonResponse({'error': 'Неверное количество'}, status=400)


# Дополнительная функция для получения счетчика активных инструментов
def get_active_equipment_count(request):
    """API endpoint для получения количества активных инструментов"""
    count = Equipment.objects.filter(is_active=True).count()
    return JsonResponse({'active_equipment_count': count})


# Модельный метод для получения счетчика (опционально)
def get_active_equipment_count_model():
    """Функция для получения количества активных инструментов из модели"""
    return Equipment.objects.filter(is_active=True).count()