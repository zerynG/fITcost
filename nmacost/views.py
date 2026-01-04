from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from io import BytesIO

# Проверка доступности библиотек
try:
    from xhtml2pdf import pisa
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping

    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from docx import Document

    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

from .models import NMACost, ResourceItem
from .forms import NMACostForm, ResourceItemForm


@login_required
def nmacost_list(request, workspace_id=None, project_id=None):
    """Список всех записей НМА с фильтрацией по проекту"""
    from workspace.models import Project
    
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Показываем НМА только для текущего проекта
        nmacosts = NMACost.objects.filter(project=project).prefetch_related('resources')
    else:
        project = None
        # Показываем все НМА, если проект не указан
        nmacosts = NMACost.objects.all().prefetch_related('resources')

    # Статистика
    total_resources = ResourceItem.objects.filter(nmacost__in=nmacosts).count()
    total_cost_result = nmacosts.aggregate(total=Sum('total_cost'))
    total_cost = total_cost_result['total'] or 0

    # Пагинация
    paginator = Paginator(nmacosts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'nmacost/nmacost_list.html', {
        'page_obj': page_obj,
        'total_resources': total_resources,
        'total_cost': total_cost,
        'has_pdf': HAS_PDF,
        'has_pandas': HAS_PANDAS,
        'has_docx': HAS_DOCX,
        'project_id': project_id,
        'workspace_id': workspace_id,
        'project': project,
    })


@login_required
def nmacost_detail(request, nmacost_id):
    """Детальная страница конкретной записи НМА"""
    nmacost = get_object_or_404(NMACost, id=nmacost_id)
    resources = nmacost.resources.all()
    
    # Получаем workspace_id и project_id для сайдбара
    workspace_id = None
    project_id = None
    if nmacost.project and hasattr(nmacost.project, 'workspace'):
        workspace_id = nmacost.project.workspace.id
        project_id = nmacost.project.id

    return render(request, 'nmacost/nmacost_detail.html', {
        'nmacost': nmacost,
        'resources': resources,
        'has_pdf': HAS_PDF,
        'has_pandas': HAS_PANDAS,
        'has_docx': HAS_DOCX,
        'workspace_id': workspace_id,
        'project_id': project_id,
    })


@login_required
def nmacost_create(request, workspace_id=None, project_id=None):
    """Создание новой записи НМА"""
    from workspace.models import Project
    
    project = None
    if project_id:
        project = Project.objects.filter(id=project_id).first()
    
    if request.method == 'POST':
        form = NMACostForm(request.POST)
        if form.is_valid():
            nmacost = form.save(commit=False)
            if project:
                nmacost.project = project
            nmacost.total_cost = 0  # Начальная стоимость
            nmacost.save()
            if project_id and workspace_id:
                return redirect('nmacost:nmacost-list-project', workspace_id=workspace_id, project_id=project_id)
            return redirect('nmacost:nmacost-detail', nmacost_id=nmacost.id)
    else:
        form = NMACostForm()
        if project:
            form.fields['project'].initial = project

    return render(request, 'nmacost/nmacost_form.html', {
        'form': form,
        'title': 'Создание стоимости НМА',
        'project_id': project_id,
        'workspace_id': workspace_id,
        'project': project,
    })


@login_required
def nmacost_edit(request, nmacost_id, workspace_id=None, project_id=None):
    """Редактирование записи НМА"""
    nmacost = get_object_or_404(NMACost, id=nmacost_id)
    # Если project_id не передан, пытаемся получить из nmacost
    if not project_id and nmacost.project:
        project_id = nmacost.project.id
        if nmacost.project.workspace:
            workspace_id = nmacost.project.workspace.id

    if request.method == 'POST':
        form = NMACostForm(request.POST, instance=nmacost)
        if form.is_valid():
            form.save()
            if project_id and workspace_id:
                return redirect('nmacost:nmacost-detail', nmacost_id=nmacost.id)
            return redirect('nmacost:nmacost-detail', nmacost_id=nmacost.id)
    else:
        form = NMACostForm(instance=nmacost)

    return render(request, 'nmacost/nmacost_form.html', {
        'form': form,
        'title': 'Редактирование стоимости НМА',
        'nmacost': nmacost,
        'project_id': project_id,
        'workspace_id': workspace_id,
    })


@login_required
def resource_add(request, nmacost_id):
    """Добавление ресурса к записи НМА"""
    nmacost = get_object_or_404(NMACost, id=nmacost_id)

    if request.method == 'POST':
        form = ResourceItemForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.nmacost = nmacost
            resource.save()  # total_cost рассчитывается автоматически в save() модели

            # Пересчитываем общую стоимость НМА
            total = sum(res.total_cost for res in nmacost.resources.all())
            nmacost.total_cost = total
            nmacost.save()

            return redirect('nmacost:nmacost-detail', nmacost_id=nmacost.id)
    else:
        form = ResourceItemForm()

    return render(request, 'nmacost/resource_form.html', {
        'form': form,
        'nmacost': nmacost
    })


@login_required
def export_pdf(request, nmacost_id):
    """Экспорт в PDF"""
    if not HAS_PDF:
        return HttpResponse("PDF export is not available. Please install xhtml2pdf.")

    nmacost = get_object_or_404(NMACost, id=nmacost_id)
    resources = nmacost.resources.all()

    html_string = render_to_string('nmacost/export_pdf.html', {
        'nmacost': nmacost,
        'resources': resources
    })

    result = BytesIO()
    
    # Используем правильную кодировку для кириллицы
    # xhtml2pdf требует строку в UTF-8, не BytesIO
    # Передаем строку напрямую, а не в BytesIO
    pdf = pisa.pisaDocument(
        html_string,
        result
    )

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="nmacost_{nmacost.id}.pdf"'
        return response

    return HttpResponse(f'Ошибка при создании PDF: {pdf.err}')


@login_required
def export_excel(request, nmacost_id):
    """Экспорт в Excel"""
    if not HAS_PANDAS:
        return HttpResponse("Excel export is not available. Please install pandas and openpyxl.")

    nmacost = get_object_or_404(NMACost, id=nmacost_id)
    resources = nmacost.resources.all()

    # Создаем простой CSV если нет pandas
    import csv
    from django.utils.encoding import smart_str

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="nmacost_{nmacost.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Наименование', 'Описание', 'Количество', 'Единица', 'Цена за единицу', 'Общая стоимость'])

    for resource in resources:
        writer.writerow([
            smart_str(resource.name),
            smart_str(resource.description),
            resource.quantity,
            smart_str(resource.unit),
            resource.unit_cost,
            resource.total_cost
        ])

    return response


@login_required
def export_word(request, nmacost_id):
    """Экспорт в Word"""
    nmacost = get_object_or_404(NMACost, id=nmacost_id)
    resources = nmacost.resources.all()

    # Создаем простой текстовый файл
    project_name = nmacost.project.name if nmacost.project else "Без проекта"
    content = f"Стоимость НМА: {project_name}\n"
    content += f"Срок разработки: {nmacost.development_period}\n"
    content += f"Итоговая стоимость: {nmacost.total_cost} руб.\n\n"
    content += "Ресурсы:\n"

    for resource in resources:
        content += f"- {resource.name}: {resource.quantity} {resource.unit} × {resource.unit_cost} руб. = {resource.total_cost} руб.\n"
        if resource.description:
            content += f"  Описание: {resource.description}\n"

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="nmacost_{nmacost.id}.txt"'
    return response


@login_required
def nmacost_delete(request, nmacost_id, workspace_id=None, project_id=None):
    """Удаление записи НМА"""
    nmacost = get_object_or_404(NMACost, id=nmacost_id)
    # Если project_id не передан, пытаемся получить из nmacost
    if not project_id and nmacost.project:
        project_id = nmacost.project.id
        if nmacost.project.workspace:
            workspace_id = nmacost.project.workspace.id

    if request.method == 'POST':
        project_name = nmacost.project.name if nmacost.project else "Без проекта"
        nmacost.delete()
        messages.success(request, f'Стоимость НМА "{project_name}" успешно удалена!')
        if project_id and workspace_id:
            return redirect('nmacost:nmacost-list-project', workspace_id=workspace_id, project_id=project_id)
        return redirect('nmacost:nmacost-list')

    return render(request, 'nmacost/nmacost_confirm_delete.html', {
        'nmacost': nmacost,
        'project_id': project_id,
        'workspace_id': workspace_id,
    })


@login_required
def resource_delete(request, nmacost_id, resource_id):
    """Удаление ресурса из записи НМА"""
    nmacost = get_object_or_404(NMACost, id=nmacost_id)
    resource = get_object_or_404(ResourceItem, id=resource_id, nmacost=nmacost)

    # Получаем project_id и workspace_id для редиректа
    project_id = None
    workspace_id = None
    if nmacost.project:
        project_id = nmacost.project.id
        if nmacost.project.workspace:
            workspace_id = nmacost.project.workspace.id

    # Удаляем ресурс (работает и для GET и для POST)
    resource.delete()
    # Пересчитываем общую стоимость НМА
    total = sum(res.total_cost for res in nmacost.resources.all())
    nmacost.total_cost = total
    nmacost.save()
    messages.success(request, 'Ресурс успешно удален!')
    
    # Перенаправляем обратно на детальную страницу НМА (она сама определяет правильный список)
    return redirect('nmacost:nmacost-detail', nmacost_id=nmacost.id)