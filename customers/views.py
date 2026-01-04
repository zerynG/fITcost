from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Customer
from .forms import CustomerForm
from workspace.models import Project, Workspace


@login_required
def customer_list(request, workspace_id=None, project_id=None):
    """Список заказчиков с фильтрацией по проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Показываем заказчиков из текущего проекта + те, которые можно использовать в других проектах
        customers = Customer.objects.filter(
            Q(project=project) | Q(can_be_shared=True, project__workspace=project.workspace)
        ).distinct()
    else:
        customers = Customer.objects.all()
    
    context = {
        'customers': customers,
        'project_id': project_id,
        'workspace_id': workspace_id,
    }
    return render(request, 'customers/customer_list.html', context)


@login_required
def customer_create(request, workspace_id=None, project_id=None):
    """Создание заказчика с привязкой к проекту"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = None
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            if project_id:
                customer.project = project
            customer.save()
            messages.success(request, 'Заказчик успешно создан')
            if project_id:
                return redirect('customers:customer_list_project', workspace_id=workspace_id, project_id=project_id)
            else:
                return redirect('customers:customer_list')
    else:
        form = CustomerForm()
        if project_id:
            # Устанавливаем project в форме через initial
            form.initial['project'] = project
    
    context = {
        'form': form,
        'project_id': project_id,
        'workspace_id': workspace_id,
        'project': project,
    }
    return render(request, 'customers/customer_form.html', context)


class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Заказчик успешно обновлен')
        customer = form.save()
        # Проверяем, есть ли project_id в URL
        project_id = self.kwargs.get('project_id')
        workspace_id = self.kwargs.get('workspace_id')
        if project_id and workspace_id:
            return redirect('customers:customer_list_project', workspace_id=workspace_id, project_id=project_id)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_id'] = self.kwargs.get('project_id')
        context['workspace_id'] = self.kwargs.get('workspace_id')
        return context


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Заказчик успешно удален')
        # Получаем customer для определения project_id
        customer = self.get_object()
        # Проверяем, есть ли project_id в URL, если нет - пытаемся получить из объекта
        project_id = self.kwargs.get('project_id')
        workspace_id = self.kwargs.get('workspace_id')
        
        # Если project_id не передан в URL, пытаемся получить из customer
        if not project_id and customer.project:
            project_id = customer.project.id
            if customer.project.workspace:
                workspace_id = customer.project.workspace.id
        
        super().delete(request, *args, **kwargs)
        if project_id and workspace_id:
            return redirect('customers:customer_list_project', workspace_id=workspace_id, project_id=project_id)
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_id'] = self.kwargs.get('project_id')
        context['workspace_id'] = self.kwargs.get('workspace_id')
        return context