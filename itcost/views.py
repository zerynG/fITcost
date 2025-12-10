from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import CostCalculationForm, OrganizationSettingsForm, RoleAssignmentForm
from .models import CostCalculation, OrganizationSettings, RoleAssignment

# Импортируем формы из других приложений
try:
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class CostDashboardView(LoginRequiredMixin, ListView):
    """Сводный дашборд по расчетам и ролям."""

    model = CostCalculation
    template_name = "itcost/dashboard.html"
    context_object_name = "calculations"
    paginate_by = 10

    def get_queryset(self):
        return CostCalculation.objects.select_related("created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        aggregates = qs.aggregate(
            development_total=Sum("development_cost"),
            intangible_total=Sum("intangible_asset_cost"),
            commercial_total=Sum("commercial_offer_cost"),
        )
        context["metrics"] = {
            "development_total": aggregates["development_total"] or Decimal("0.00"),
            "intangible_total": aggregates["intangible_total"] or Decimal("0.00"),
            "commercial_total": aggregates["commercial_total"] or Decimal("0.00"),
            "projects_count": qs.count(),
        }
        context["organization_settings"] = OrganizationSettings.objects.first()
        role_labels = dict(RoleAssignment.ROLE_CHOICES)
        role_summary = RoleAssignment.objects.values("role").annotate(
            total=Count("role")
        )
        context["role_breakdown"] = [
            {"label": role_labels.get(item["role"], item["role"]), "total": item["total"]}
            for item in role_summary
        ]
        return context


class CostCalculationCreateView(LoginRequiredMixin, TemplateView):
    template_name = "itcost/cost_calculation_form.html"
    form_class = CostCalculationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {"form": form}
        
        # Добавляем формы для создания НМА и коммерческого предложения
        if HAS_NMA:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # Создаем копию данных для модификации (copy() создает мутабельную копию QueryDict)
        form_data = request.POST.copy()
        context = {}
        
        # Удаляем скрытые поля из исходных данных, чтобы установить их правильно
        if 'nma_cost' in form_data:
            form_data.pop('nma_cost')
        if 'commercial_proposal' in form_data:
            form_data.pop('commercial_proposal')
        
        # Обработка создания новой формы НМА
        nma_cost = None
        if HAS_NMA and form_data.get("nma_source") == "new":
            nma_form = NMACostForm(request.POST)
            context["nma_form"] = nma_form
            if nma_form.is_valid():
                nma_cost = nma_form.save(commit=False)
                nma_cost.total_cost = 0
                nma_cost.save()
                # Правильно устанавливаем значение в QueryDict
                form_data.setlist('nma_cost', [str(nma_cost.pk)])
            else:
                # Если форма НМА невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_COMMERCIAL:
                    context["commercial_form"] = CommercialProposalForm()
                    context["service_formset"] = ServiceItemFormSet()
                return self.render_to_response(context)
        elif HAS_NMA and form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Устанавливаем пустое значение, если значение невалидно
                    form_data.setlist('nma_cost', [''])
            else:
                # Устанавливаем пустое значение, если не выбрано
                form_data.setlist('nma_cost', [''])
        else:
            # Устанавливаем пустое значение, если не используется или HAS_NMA = False
            # ВАЖНО: всегда устанавливаем пустое значение для скрытого поля
            form_data.setlist('nma_cost', [''])
        
        # Обработка создания нового коммерческого предложения
        commercial_proposal = None
        if HAS_COMMERCIAL and form_data.get("commercial_source") == "new":
            commercial_form = CommercialProposalForm(request.POST)
            service_formset = ServiceItemFormSet(request.POST)
            context["commercial_form"] = commercial_form
            context["service_formset"] = service_formset
            if commercial_form.is_valid() and service_formset.is_valid():
                commercial_proposal = commercial_form.save()
                service_formset.instance = commercial_proposal
                service_formset.save()
                # Правильно устанавливаем значение в QueryDict
                form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
            else:
                # Если форма коммерческого предложения невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_NMA and "nma_form" not in context:
                    context["nma_form"] = NMACostForm()
                return self.render_to_response(context)
        elif HAS_COMMERCIAL and form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    # Устанавливаем пустое значение, если значение невалидно
                    form_data.setlist('commercial_proposal', [''])
            else:
                # Устанавливаем пустое значение, если не выбрано
                form_data.setlist('commercial_proposal', [''])
        else:
            # Устанавливаем пустое значение, если не используется или HAS_COMMERCIAL = False
            # ВАЖНО: всегда устанавливаем пустое значение для скрытого поля
            form_data.setlist('commercial_proposal', [''])
        
        # Гарантируем, что скрытые поля всегда присутствуют в form_data
        # Это критически важно для корректной валидации формы
        if 'nma_cost' not in form_data:
            form_data.setlist('nma_cost', [''])
        if 'commercial_proposal' not in form_data:
            form_data.setlist('commercial_proposal', [''])
        
        # Создаем форму с обновленными данными
        # QueryDict уже обработан выше, пустые значения установлены
        form = self.form_class(form_data)
        context["form"] = form
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            calculation.nma_cost = nma_cost if nma_cost else None
            calculation.commercial_proposal = commercial_proposal if commercial_proposal else None
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
        # Добавляем сообщение об ошибках валидации с детальной информацией
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            # Выводим все ошибки для отладки
            error_text = "; ".join(error_messages)
            messages.error(request, f"Пожалуйста, исправьте ошибки в форме: {error_text}")
            # Также логируем в консоль для отладки
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Form validation errors: {form.errors}")
            logger.error(f"Form data keys: {list(form_data.keys())}")
            logger.error(f"nma_source: {form_data.get('nma_source')}, commercial_source: {form_data.get('commercial_source')}")
            logger.error(f"nma_cost in form_data: {'nma_cost' in form_data}, commercial_proposal in form_data: {'commercial_proposal' in form_data}")
            if 'nma_cost' in form_data:
                logger.error(f"nma_cost value: {form_data.get('nma_cost')}")
            if 'commercial_proposal' in form_data:
                logger.error(f"commercial_proposal value: {form_data.get('commercial_proposal')}")
        
        return self.render_to_response(context)


class CostCalculationDetailView(LoginRequiredMixin, DetailView):
    model = CostCalculation
    template_name = "itcost/cost_calculation_detail.html"
    context_object_name = "calculation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["components"] = self.object.calculate_components()
        return context


class CostCalculationUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "itcost/cost_calculation_form.html"
    form_class = CostCalculationForm

    def get_object(self):
        return CostCalculation.objects.get(pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        calculation = self.get_object()
        form = self.form_class(instance=calculation)
        context = {"form": form, "calculation": calculation}
        
        # Добавляем формы для создания НМА и коммерческого предложения
        if HAS_NMA:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        calculation = self.get_object()
        form = self.form_class(request.POST, instance=calculation)
        context = {"form": form, "calculation": calculation}
        
        # Обработка создания новой формы НМА
        nma_cost = None
        if HAS_NMA and form.data.get("nma_source") == "new":
            nma_form = NMACostForm(request.POST)
            context["nma_form"] = nma_form
            if nma_form.is_valid():
                nma_cost = nma_form.save(commit=False)
                nma_cost.total_cost = 0
                nma_cost.save()
            else:
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except (NMACost.DoesNotExist, ValueError):
                    pass
        elif form.data.get("nma_source") == "none":
            nma_cost = None
        
        # Обработка создания нового коммерческого предложения
        commercial_proposal = None
        if HAS_COMMERCIAL and form.data.get("commercial_source") == "new":
            commercial_form = CommercialProposalForm(request.POST)
            service_formset = ServiceItemFormSet(request.POST)
            context["commercial_form"] = commercial_form
            context["service_formset"] = service_formset
            if commercial_form.is_valid() and service_formset.is_valid():
                commercial_proposal = commercial_form.save()
                service_formset.instance = commercial_proposal
                service_formset.save()
            else:
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id and commercial_id != '':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except (CommercialProposal.DoesNotExist, ValueError):
                    pass
        elif form.data.get("commercial_source") == "none":
            commercial_proposal = None
        
        # Создаем копию данных формы для установки значений скрытых полей
        form_data = request.POST.copy()
        
        # Устанавливаем значения скрытых полей
        if nma_cost is not None:
            form_data['nma_cost'] = str(nma_cost.pk) if nma_cost else ""
        else:
            form_data['nma_cost'] = ""
        
        if commercial_proposal is not None:
            form_data['commercial_proposal'] = str(commercial_proposal.pk) if commercial_proposal else ""
        else:
            form_data['commercial_proposal'] = ""
        
        # Создаем новую форму с обновленными данными
        form = self.form_class(form_data, instance=calculation)
        context["form"] = form
        
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            # Привязываем созданные или выбранные формы
            if nma_cost is not None:
                updated.nma_cost = nma_cost
            else:
                updated.nma_cost = None
            if commercial_proposal is not None:
                updated.commercial_proposal = commercial_proposal
            else:
                updated.commercial_proposal = None
            updated.save()
            messages.success(request, "Расчет обновлен.")
            return redirect("itcost:calculation_detail", pk=updated.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
        return self.render_to_response(context)


class OrganizationSettingsUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "itcost/organization_settings_form.html"
    form_class = OrganizationSettingsForm
    success_url = reverse_lazy("itcost:settings")

    def get_object(self, queryset=None):
        settings_obj, _ = OrganizationSettings.objects.get_or_create(
            pk=1,
            defaults={
                "company_name": "",
                "director_full_name": "",
                "director_position": "",
                "contact_phone": "",
                "contact_email": "",
            },
        )
        return settings_obj

    def form_valid(self, form):
        messages.success(self.request, "Настройки организации обновлены.")
        return super().form_valid(form)


class RoleAssignmentView(LoginRequiredMixin, FormView):
    template_name = "itcost/role_assignment.html"
    form_class = RoleAssignmentForm
    success_url = reverse_lazy("itcost:roles")

    def form_valid(self, form):
        assignment = form.save(commit=False)
        assignment.assigned_by = self.request.user
        try:
            assignment.save()
            messages.success(self.request, "Роль назначена.")
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "Такая роль уже назначена выбранному пользователю.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignments"] = RoleAssignment.objects.select_related(
            "user", "assigned_by"
        )
        return context


class CostCalculationDeleteView(LoginRequiredMixin, TemplateView):
    """Удаление расчета стоимости проекта."""
    
    template_name = "itcost/cost_calculation_confirm_delete.html"
    
    def get_object(self):
        return get_object_or_404(CostCalculation, pk=self.kwargs["pk"])
    
    def get(self, request, *args, **kwargs):
        calculation = self.get_object()
        return self.render_to_response({"calculation": calculation})
    
    def post(self, request, *args, **kwargs):
        calculation = self.get_object()
        project_name = calculation.project_name
        calculation.delete()
        messages.success(request, f'Расчет стоимости "{project_name}" успешно удален!')
        return redirect("itcost:dashboard")

