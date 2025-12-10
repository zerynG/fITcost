# Добавление приложения для расчета стоимости
_Exported on 02.12.2025 at 4:17:51 GMT+3 from Cursor (2.0.77)_

---

**User**

добавь в проект приложение соответствующее тз Система расчета стоимости IT-проекта - система расчет стоимости разработки программного обеспечения, которая позволяет исходя из введенных показателей рассчитывать 3 ключевых показателя:

- Стоимость разработки проекта;

- Стоимость нематериального актива (стоимость IT-решения, которое ставится на баланс, если это разработка продукта);

- Стоимость коммерческого предложения;

Основные участники системы:

- Глобальный администратор;

- Коммерческий директор;

- Бухгалтер;

- Кадровик;

Участники (роли) могут быть у одного пользователя.

Основные настройки системы:

- Название компании;

- ФИО руководителя;

- Должность руководителя;

- Логотип предприятия;

- Контактный телефон;

- Контактный email;

---

**Cursor**

```python
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class OrganizationSettings(models.Model):
    """Глобальные настройки компании, влияющие на расчеты и документы."""

    company_name = models.CharField(max_length=255, verbose_name="Название компании")
    director_full_name = models.CharField(max_length=255, verbose_name="ФИО руководителя")
    director_position = models.CharField(max_length=255, verbose_name="Должность руководителя")
    logo = models.ImageField(
        upload_to="organization_logos/",
        verbose_name="Логотип предприятия",
        blank=True,
        null=True,
    )
    contact_phone = models.CharField(max_length=32, verbose_name="Контактный телефон")
    contact_email = models.EmailField(verbose_name="Контактный email")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Настройки организации"
        verbose_name_plural = "Настройки организации"

    def __str__(self) -> str:
        return self.company_name or "Настройки организации"


class CostCalculation(models.Model):
    """Расчет стоимости проекта с ключевыми показателями."""

    project_name = models.CharField(max_length=255, verbose_name="Название проекта")
    client_name = models.CharField(
        max_length=255, verbose_name="Заказчик", blank=True
    )
    project_brief = models.TextField(verbose_name="Описание/ТЗ", blank=True)
    estimated_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Трудоемкость, ч",
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Ставка, ₽/ч",
    )
    infrastructure_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Инфраструктурные затраты",
    )
    other_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Прочие расходы",
    )
    management_overhead_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("15.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Управленческие расходы, %",
    )
    risk_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Риск, %",
    )
    profit_margin_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("200.00")),
        ],
        verbose_name="Маржа прибыли, %",
    )
    asset_capitalization_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("80.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Доля капитализации НМА, %",
    )
    commercial_markup_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("300.00")),
        ],
        verbose_name="Наценка коммерческого предложения, %",
    )
    development_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость разработки проекта",
        editable=False,
    )
    intangible_asset_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость нематериального актива",
        editable=False,
    )
    commercial_offer_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость коммерческого предложения",
        editable=False,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="cost_calculations",
        verbose_name="Инициатор",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Расчет стоимости"
        verbose_name_plural = "Расчеты стоимости"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.project_name} — {self.development_cost} ₽"

    # ---- расчетные методы ----
    def calculate_components(self) -> dict:
        base_labor = self.estimated_hours * self.hourly_rate
        management_overhead = base_labor * (
            self.management_overhead_percent / Decimal("100")
        )
        risk_reserve = base_labor * (self.risk_percent / Decimal("100"))
        profit_margin = base_labor * (self.profit_margin_percent / Decimal("100"))

        development_cost = (
            base_labor
            + management_overhead
            + risk_reserve
            + profit_margin
            + self.infrastructure_cost
            + self.other_expenses
        )
        intangible_asset = development_cost * (
            self.asset_capitalization_percent / Decimal("100")
        )
        commercial_offer = development_cost * (
            Decimal("1") + self.commercial_markup_percent / Decimal("100")
        )
        return {
            "base_labor": base_labor,
            "management_overhead": management_overhead,
            "risk_reserve": risk_reserve,
            "profit_margin": profit_margin,
            "development_cost": development_cost,
            "intangible_asset": intangible_asset,
            "commercial_offer": commercial_offer,
        }

    def save(self, *args, **kwargs):
        components = self.calculate_components()
        self.development_cost = components["development_cost"]
        self.intangible_asset_cost = components["intangible_asset"]
        self.commercial_offer_cost = components["commercial_offer"]
        super().save(*args, **kwargs)


class RoleAssignment(models.Model):
    """Привязка ролей участников системы к пользователям."""

    GLOBAL_ADMIN = "global_admin"
    COMMERCIAL_DIRECTOR = "commercial_director"
    ACCOUNTANT = "accountant"
    HR_SPECIALIST = "hr_specialist"

    ROLE_CHOICES = [
        (GLOBAL_ADMIN, "Глобальный администратор"),
        (COMMERCIAL_DIRECTOR, "Коммерческий директор"),
        (ACCOUNTANT, "Бухгалтер"),
        (HR_SPECIALIST, "Кадровик"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="itcost_roles"
    )
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_itcost_roles",
        verbose_name="Назначил",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Роль в системе расчета"
        verbose_name_plural = "Роли в системе расчета"
        unique_together = ("user", "role")
        ordering = ("-assigned_at",)

    def __str__(self) -> str:
        return f"{self.user} — {self.get_role_display()}"

```

```python
from django.apps import AppConfig


class ItcostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'itcost'
    verbose_name = "Система расчета стоимости"

```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()


class CostCalculationForm(forms.ModelForm):
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
        }


class OrganizationSettingsForm(forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }

```

```python
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class OrganizationSettings(models.Model):
    """Глобальные настройки компании, влияющие на расчеты и документы."""

    company_name = models.CharField(
        max_length=255, verbose_name="Название компании", blank=True
    )
    director_full_name = models.CharField(
        max_length=255, verbose_name="ФИО руководителя", blank=True
    )
    director_position = models.CharField(
        max_length=255, verbose_name="Должность руководителя", blank=True
    )
    logo = models.ImageField(
        upload_to="organization_logos/",
        verbose_name="Логотип предприятия",
        blank=True,
        null=True,
    )
    contact_phone = models.CharField(
        max_length=32, verbose_name="Контактный телефон", blank=True
    )
    contact_email = models.EmailField(verbose_name="Контактный email", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Настройки организации"
        verbose_name_plural = "Настройки организации"

    def __str__(self) -> str:
        return self.company_name or "Настройки организации"


class CostCalculation(models.Model):
    """Расчет стоимости проекта с ключевыми показателями."""

    project_name = models.CharField(max_length=255, verbose_name="Название проекта")
    client_name = models.CharField(
        max_length=255, verbose_name="Заказчик", blank=True
    )
    project_brief = models.TextField(verbose_name="Описание/ТЗ", blank=True)
    estimated_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Трудоемкость, ч",
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Ставка, ₽/ч",
    )
    infrastructure_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Инфраструктурные затраты",
    )
    other_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Прочие расходы",
    )
    management_overhead_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("15.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Управленческие расходы, %",
    )
    risk_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Риск, %",
    )
    profit_margin_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("200.00")),
        ],
        verbose_name="Маржа прибыли, %",
    )
    asset_capitalization_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("80.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Доля капитализации НМА, %",
    )
    commercial_markup_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("300.00")),
        ],
        verbose_name="Наценка коммерческого предложения, %",
    )
    development_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость разработки проекта",
        editable=False,
    )
    intangible_asset_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость нематериального актива",
        editable=False,
    )
    commercial_offer_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость коммерческого предложения",
        editable=False,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="cost_calculations",
        verbose_name="Инициатор",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Расчет стоимости"
        verbose_name_plural = "Расчеты стоимости"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.project_name} — {self.development_cost} ₽"

    # ---- расчетные методы ----
    def calculate_components(self) -> dict:
        base_labor = self.estimated_hours * self.hourly_rate
        management_overhead = base_labor * (
            self.management_overhead_percent / Decimal("100")
        )
        risk_reserve = base_labor * (self.risk_percent / Decimal("100"))
        profit_margin = base_labor * (self.profit_margin_percent / Decimal("100"))

        development_cost = (
            base_labor
            + management_overhead
            + risk_reserve
            + profit_margin
            + self.infrastructure_cost
            + self.other_expenses
        )
        intangible_asset = development_cost * (
            self.asset_capitalization_percent / Decimal("100")
        )
        commercial_offer = development_cost * (
            Decimal("1") + self.commercial_markup_percent / Decimal("100")
        )
        return {
            "base_labor": base_labor,
            "management_overhead": management_overhead,
            "risk_reserve": risk_reserve,
            "profit_margin": profit_margin,
            "development_cost": development_cost,
            "intangible_asset": intangible_asset,
            "commercial_offer": commercial_offer,
        }

    def save(self, *args, **kwargs):
        components = self.calculate_components()
        self.development_cost = components["development_cost"]
        self.intangible_asset_cost = components["intangible_asset"]
        self.commercial_offer_cost = components["commercial_offer"]
        super().save(*args, **kwargs)


class RoleAssignment(models.Model):
    """Привязка ролей участников системы к пользователям."""

    GLOBAL_ADMIN = "global_admin"
    COMMERCIAL_DIRECTOR = "commercial_director"
    ACCOUNTANT = "accountant"
    HR_SPECIALIST = "hr_specialist"

    ROLE_CHOICES = [
        (GLOBAL_ADMIN, "Глобальный администратор"),
        (COMMERCIAL_DIRECTOR, "Коммерческий директор"),
        (ACCOUNTANT, "Бухгалтер"),
        (HR_SPECIALIST, "Кадровик"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="itcost_roles"
    )
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_itcost_roles",
        verbose_name="Назначил",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Роль в системе расчета"
        verbose_name_plural = "Роли в системе расчета"
        unique_together = ("user", "role")
        ordering = ("-assigned_at",)

    def __str__(self) -> str:
        return f"{self.user} — {self.get_role_display()}"

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        context["role_summary"] = RoleAssignment.objects.values("role").annotate(
            total=Count("role")
        )
        context["role_labels"] = dict(RoleAssignment.ROLE_CHOICES)
        return context


class CostCalculationCreateView(LoginRequiredMixin, TemplateView):
    template_name = "itcost/cost_calculation_form.html"
    form_class = CostCalculationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return self.render_to_response({"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        return self.render_to_response({"form": form})


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
        return self.render_to_response({"form": form, "calculation": calculation})

    def post(self, request, *args, **kwargs):
        calculation = self.get_object()
        form = self.form_class(request.POST, instance=calculation)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            updated.save()
            messages.success(request, "Расчет обновлен.")
            return redirect("itcost:calculation_detail", pk=updated.pk)
        return self.render_to_response({"form": form, "calculation": calculation})


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
        except Exception:
            messages.error(
                self.request,
                "Не удалось назначить роль. Проверьте, не дублируется ли запись.",
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignments"] = RoleAssignment.objects.select_related(
            "user", "assigned_by"
        )
        return context

```

```python
from django.urls import path

from . import views

app_name = "itcost"

urlpatterns = [
    path("", views.CostDashboardView.as_view(), name="dashboard"),
    path(
        "calculations/new/",
        views.CostCalculationCreateView.as_view(),
        name="calculation_create",
    ),
    path(
        "calculations/<int:pk>/",
        views.CostCalculationDetailView.as_view(),
        name="calculation_detail",
    ),
    path(
        "calculations/<int:pk>/edit/",
        views.CostCalculationUpdateView.as_view(),
        name="calculation_edit",
    ),
    path("settings/", views.OrganizationSettingsUpdateView.as_view(), name="settings"),
    path("roles/", views.RoleAssignmentView.as_view(), name="roles"),
]

```

```html
{% extends "base.html" %}

{% block title %}Дашборд расчета стоимости{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3">Система расчета стоимости IT-проекта</h1>
            <p class="text-muted mb-0">Контролируйте ключевые показатели стоимости разработки, НМА и коммерческих предложений.</p>
        </div>
        <div class="d-flex gap-2">
            <a class="btn btn-primary" href="{% url 'itcost:calculation_create' %}">
                <i class="fa-solid fa-plus me-2"></i>Новый расчет
            </a>
            <a class="btn btn-outline-secondary" href="{% url 'itcost:settings' %}">
                <i class="fa-solid fa-gear me-2"></i>Настройки
            </a>
            <a class="btn btn-outline-info" href="{% url 'itcost:roles' %}">
                <i class="fa-solid fa-users me-2"></i>Роли
            </a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Всего проектов</p>
                    <h3 class="fw-bold">{{ metrics.projects_count }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ metrics.development_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ metrics.intangible_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Коммерческие предложения</p>
                    <h3 class="fw-bold">{{ metrics.commercial_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Последние расчеты</h5>
                </div>
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead>
                            <tr>
                                <th>Проект</th>
                                <th>Заказчик</th>
                                <th>Разработка</th>
                                <th>НМА</th>
                                <th>Коммерческое</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for calc in calculations %}
                            <tr>
                                <td>
                                    <div class="fw-semibold">{{ calc.project_name }}</div>
                                    <small class="text-muted">обновлено {{ calc.updated_at|date:"d.m.Y H:i" }}</small>
                                </td>
                                <td>{{ calc.client_name|default:"—" }}</td>
                                <td>{{ calc.development_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.intangible_asset_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.commercial_offer_cost|floatformat:2 }} ₽</td>
                                <td class="text-end">
                                    <a href="{% url 'itcost:calculation_detail' calc.pk %}" class="btn btn-sm btn-outline-primary">Подробнее</a>
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="6" class="text-center py-4 text-muted">Пока нет расчетов. Создайте первый, чтобы увидеть аналитику.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Настройки компании</h5>
                </div>
                <div class="card-body">
                    {% if organization_settings %}
                        <p class="mb-1"><strong>{{ organization_settings.company_name|default:"Название не указано" }}</strong></p>
                        <p class="mb-1 text-muted">{{ organization_settings.director_full_name|default:"Руководитель не указан" }}</p>
                        <p class="mb-1">{{ organization_settings.director_position|default:"Должность не указана" }}</p>
                        <p class="mb-0">
                            <i class="fa-solid fa-phone me-2"></i>{{ organization_settings.contact_phone|default:"—" }}<br>
                            <i class="fa-solid fa-envelope me-2"></i>{{ organization_settings.contact_email|default:"—" }}
                        </p>
                    {% else %}
                        <p class="text-muted mb-0">Настройки еще не заполнены.</p>
                    {% endif %}
                </div>
            </div>

            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Ролевой состав</h5>
                </div>
                <div class="card-body">
                    {% for role in role_summary %}
                        <div class="d-flex justify-content-between mb-2">
                            <span>{{ role_labels|get_item:role.role }}</span>
                            <span class="badge bg-primary rounded-pill">{{ role.total }}</span>
                        </div>
                    {% empty %}
                        <p class="text-muted mb-0">Роли еще не назначены.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        return self.render_to_response({"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        return self.render_to_response({"form": form})


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
        return self.render_to_response({"form": form, "calculation": calculation})

    def post(self, request, *args, **kwargs):
        calculation = self.get_object()
        form = self.form_class(request.POST, instance=calculation)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            updated.save()
            messages.success(request, "Расчет обновлен.")
            return redirect("itcost:calculation_detail", pk=updated.pk)
        return self.render_to_response({"form": form, "calculation": calculation})


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
        except Exception:
            messages.error(
                self.request,
                "Не удалось назначить роль. Проверьте, не дублируется ли запись.",
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignments"] = RoleAssignment.objects.select_related(
            "user", "assigned_by"
        )
        return context

```

```html
{% extends "base.html" %}

{% block title %}Дашборд расчета стоимости{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3">Система расчета стоимости IT-проекта</h1>
            <p class="text-muted mb-0">Контролируйте ключевые показатели стоимости разработки, НМА и коммерческих предложений.</p>
        </div>
        <div class="d-flex gap-2">
            <a class="btn btn-primary" href="{% url 'itcost:calculation_create' %}">
                <i class="fa-solid fa-plus me-2"></i>Новый расчет
            </a>
            <a class="btn btn-outline-secondary" href="{% url 'itcost:settings' %}">
                <i class="fa-solid fa-gear me-2"></i>Настройки
            </a>
            <a class="btn btn-outline-info" href="{% url 'itcost:roles' %}">
                <i class="fa-solid fa-users me-2"></i>Роли
            </a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Всего проектов</p>
                    <h3 class="fw-bold">{{ metrics.projects_count }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ metrics.development_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ metrics.intangible_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Коммерческие предложения</p>
                    <h3 class="fw-bold">{{ metrics.commercial_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Последние расчеты</h5>
                </div>
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead>
                            <tr>
                                <th>Проект</th>
                                <th>Заказчик</th>
                                <th>Разработка</th>
                                <th>НМА</th>
                                <th>Коммерческое</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for calc in calculations %}
                            <tr>
                                <td>
                                    <div class="fw-semibold">{{ calc.project_name }}</div>
                                    <small class="text-muted">обновлено {{ calc.updated_at|date:"d.m.Y H:i" }}</small>
                                </td>
                                <td>{{ calc.client_name|default:"—" }}</td>
                                <td>{{ calc.development_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.intangible_asset_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.commercial_offer_cost|floatformat:2 }} ₽</td>
                                <td class="text-end">
                                    <a href="{% url 'itcost:calculation_detail' calc.pk %}" class="btn btn-sm btn-outline-primary">Подробнее</a>
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="6" class="text-center py-4 text-muted">Пока нет расчетов. Создайте первый, чтобы увидеть аналитику.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Настройки компании</h5>
                </div>
                <div class="card-body">
                    {% if organization_settings %}
                        <p class="mb-1"><strong>{{ organization_settings.company_name|default:"Название не указано" }}</strong></p>
                        <p class="mb-1 text-muted">{{ organization_settings.director_full_name|default:"Руководитель не указан" }}</p>
                        <p class="mb-1">{{ organization_settings.director_position|default:"Должность не указана" }}</p>
                        <p class="mb-0">
                            <i class="fa-solid fa-phone me-2"></i>{{ organization_settings.contact_phone|default:"—" }}<br>
                            <i class="fa-solid fa-envelope me-2"></i>{{ organization_settings.contact_email|default:"—" }}
                        </p>
                    {% else %}
                        <p class="text-muted mb-0">Настройки еще не заполнены.</p>
                    {% endif %}
                </div>
            </div>

            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Ролевой состав</h5>
                </div>
                <div class="card-body">
                    {% for role in role_breakdown %}
                        <div class="d-flex justify-content-between mb-2">
                            <span>{{ role.label }}</span>
                            <span class="badge bg-primary rounded-pill">{{ role.total }}</span>
                        </div>
                    {% empty %}
                        <p class="text-muted mb-0">Роли еще не назначены.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


```

```html
{% extends "base.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        <div class="row g-3">
                            {% for field in form %}
                                <div class="col-md-6">
                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                    {{ field }}
                                    {% if field.help_text %}
                                        <small class="text-muted">{{ field.help_text }}</small>
                                    {% endif %}
                                    {% for error in field.errors %}
                                        <div class="text-danger small">{{ error }}</div>
                                    {% endfor %}
                                </div>
                            {% endfor %}
                        </div>
                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

```

```html
{% extends "base.html" %}

{% block title %}{{ calculation.project_name }}{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3 mb-1">{{ calculation.project_name }}</h1>
            <p class="text-muted mb-0">{{ calculation.client_name|default:"Заказчик не указан" }}</p>
        </div>
        <div class="d-flex gap-2">
            <a href="{% url 'itcost:calculation_edit' calculation.pk %}" class="btn btn-outline-primary">
                <i class="fa-solid fa-pen me-2"></i>Редактировать
            </a>
            <a href="{% url 'itcost:dashboard' %}" class="btn btn-outline-secondary">К списку</a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ calculation.development_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ calculation.intangible_asset_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость коммерческого предложения</p>
                    <h3 class="fw-bold">{{ calculation.commercial_offer_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Входные данные</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <p class="text-muted mb-1">Трудоемкость</p>
                    <div>{{ calculation.estimated_hours }} ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Ставка</p>
                    <div>{{ calculation.hourly_rate }} ₽/ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Инфраструктурные затраты</p>
                    <div>{{ calculation.infrastructure_cost }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Прочие расходы</p>
                    <div>{{ calculation.other_expenses }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ calculation.management_overhead_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Риски</p>
                    <div>{{ calculation.risk_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Маржа</p>
                    <div>{{ calculation.profit_margin_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Капитализация НМА</p>
                    <div>{{ calculation.asset_capitalization_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Наценка КП</p>
                    <div>{{ calculation.commercial_markup_percent }}%</div>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Детализация расчетов</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-6">
                    <p class="text-muted mb-1">Базовая трудоемкость</p>
                    <div>{{ components.base_labor|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ components.management_overhead|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Риск-резерв</p>
                    <div>{{ components.risk_reserve|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Маржа прибыли</p>
                    <div>{{ components.profit_margin|floatformat:2 }} ₽</div>
                </div>
            </div>
            <hr>
            <p class="text-muted mb-1">Описание/ТЗ</p>
            <div>{{ calculation.project_brief|linebreaks|default:"—" }}</div>
        </div>
    </div>
</div>
{% endblock %}

```

```html
{% extends "base.html" %}

{% block title %}Настройки организации{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Основные настройки системы</h5>
                    <small class="text-muted">Данные используются в расчетах и документах.</small>
                </div>
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data">
                        {% csrf_token %}
                        {% for field in form %}
                            <div class="mb-3">
                                <label class="form-label">{{ field.label }}</label>
                                {{ field }}
                                {% for error in field.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        {% endfor %}
                        <div class="d-flex justify-content-between">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Назад</a>
                            <button type="submit" class="btn btn-primary">Сохранить</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

```

```html
{% extends "base.html" %}

{% block title %}Роли участников{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row g-4">
        <div class="col-lg-5">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Назначить роль</h5>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {% for field in form %}
                            <div class="mb-3">
                                <label class="form-label">{{ field.label }}</label>
                                {{ field }}
                                {% for error in field.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        {% endfor %}
                        <button type="submit" class="btn btn-primary w-100">Назначить</button>
                    </form>
                </div>
            </div>
        </div>
        <div class="col-lg-7">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0 d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Актуальные назначения</h5>
                    <a href="{% url 'itcost:dashboard' %}" class="btn btn-sm btn-outline-secondary">К дашборду</a>
                </div>
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead>
                            <tr>
                                <th>Пользователь</th>
                                <th>Роль</th>
                                <th>Назначил</th>
                                <th>Когда</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for assignment in assignments %}
                            <tr>
                                <td>{{ assignment.user.get_full_name|default:assignment.user.username }}</td>
                                <td>{{ assignment.get_role_display }}</td>
                                <td>{{ assignment.assigned_by.get_full_name|default:assignment.assigned_by }}</td>
                                <td>{{ assignment.assigned_at|date:"d.m.Y H:i" }}</td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="4" class="text-center text-muted py-4">Роли еще не распределены.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

```

```python
from django.contrib import admin

from .models import CostCalculation, OrganizationSettings, RoleAssignment


@admin.register(CostCalculation)
class CostCalculationAdmin(admin.ModelAdmin):
    list_display = (
        "project_name",
        "client_name",
        "development_cost",
        "intangible_asset_cost",
        "commercial_offer_cost",
        "created_at",
    )
    search_fields = ("project_name", "client_name")
    list_filter = ("created_at",)
    readonly_fields = (
        "development_cost",
        "intangible_asset_cost",
        "commercial_offer_cost",
        "created_at",
        "updated_at",
    )


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "director_full_name",
        "director_position",
        "contact_phone",
        "contact_email",
        "updated_at",
    )


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__first_name", "user__last_name")

```

```python
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()


class CostCalculationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="12345")

    def test_components_are_recalculated_on_save(self):
        calculation = CostCalculation.objects.create(
            project_name="Test Project",
            client_name="ACME",
            estimated_hours=Decimal("100"),
            hourly_rate=Decimal("1500"),
            infrastructure_cost=Decimal("50000"),
            other_expenses=Decimal("25000"),
            management_overhead_percent=Decimal("10"),
            risk_percent=Decimal("5"),
            profit_margin_percent=Decimal("15"),
            asset_capitalization_percent=Decimal("70"),
            commercial_markup_percent=Decimal("20"),
            created_by=self.user,
        )

        components = calculation.calculate_components()

        self.assertEqual(calculation.development_cost, components["development_cost"])
        self.assertEqual(
            calculation.intangible_asset_cost, components["intangible_asset"]
        )
        self.assertEqual(
            calculation.commercial_offer_cost, components["commercial_offer"]
        )


class OrganizationSettingsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewer", password="12345")

    def test_settings_created_implicitly(self):
        self.client.login(username="viewer", password="12345")
        response = self.client.get(reverse("itcost:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(OrganizationSettings.objects.exists())


class RoleAssignmentTests(TestCase):
    def setUp(self):
        self.assigner = User.objects.create_user(username="assigner", password="12345")
        self.target = User.objects.create_user(username="target", password="12345")

    def test_role_assignment_unique(self):
        RoleAssignment.objects.create(
            user=self.target,
            role=RoleAssignment.GLOBAL_ADMIN,
            assigned_by=self.assigner,
        )
        with self.assertRaises(Exception):
            RoleAssignment.objects.create(
                user=self.target,
                role=RoleAssignment.GLOBAL_ADMIN,
                assigned_by=self.assigner,
            )

```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
        }


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
        }


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Система расчета стоимости IT-проекта</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{% static 'css/dark-theme.css' %}" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --accent: #f72585;
            --light: #4cc9f0;
            --dark: #1d3557;
            --success: #4ade80;
            --warning: #f59e0b;
            --danger: #ef4444;
            --gradient: linear-gradient(135deg, #4361ee, #3a0ca3, #7209b7);
            --gradient-light: linear-gradient(135deg, #4cc9f0, #4361ee);
            --text-dark: #1e293b;
            --text-light: #64748b;
            --bg-light: #f8fafc;
            --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-light);
            min-height: 100vh;
            color: var(--text-dark);
            line-height: 1.6;
        }

        .header {
            background: var(--gradient);
            padding: 15px 30px;
            box-shadow: var(--shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
            opacity: 0.1;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 15px;
            z-index: 1;
        }

        .logo {
            width: 60px;
            height: 60px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 24px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .company-info h1 {
            font-size: 28px;
            color: white;
            margin-bottom: 5px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .company-contacts {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            display: flex;
            gap: 15px;
        }

        .company-contacts div {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
            z-index: 1;
        }

        .user-welcome {
            text-align: right;
        }

        .user-welcome .username {
            font-weight: bold;
            color: white;
            font-size: 16px;
        }

        .user-welcome .role {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.8);
        }

        .btn {
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .btn-logout {
            background: rgba(239, 68, 68, 0.8);
            border-color: rgba(239, 68, 68, 0.5);
        }

        .btn-logout:hover {
            background: rgba(239, 68, 68, 0.9);
        }

        .navigation {
            background: white;
            padding: 0 30px;
            box-shadow: var(--shadow);
            margin-bottom: 30px;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        /* Темная тема для home.html */
        [data-theme="dark"] body {
            background: #1a1a1a;
            color: #e0e0e0;
        }

        [data-theme="dark"] .navigation {
            background: #2d2d2d !important;
            border-bottom: 1px solid #404040;
        }

        [data-theme="dark"] .tab {
            color: #b0b0b0 !important;
        }

        [data-theme="dark"] .tab:hover {
            color: #4cc9f0 !important;
            background: rgba(76, 201, 240, 0.1) !important;
        }

        [data-theme="dark"] .tab.active {
            color: #4cc9f0 !important;
            border-bottom-color: #4cc9f0 !important;
        }

        [data-theme="dark"] .welcome-section,
        [data-theme="dark"] .calculator-section,
        [data-theme="dark"] .about-section {
            background: #2d2d2d !important;
            color: #e0e0e0 !important;
            border-color: #404040 !important;
        }

        [data-theme="dark"] .form-control,
        [data-theme="dark"] .form-group select {
            background: #3a3a3a !important;
            border-color: #404040 !important;
            color: #e0e0e0 !important;
        }

        [data-theme="dark"] .form-control:focus,
        [data-theme="dark"] .form-group select:focus {
            background: #3a3a3a !important;
            border-color: #4cc9f0 !important;
            color: #e0e0e0 !important;
        }

        [data-theme="dark"] .btn-calculate {
            background: #4361ee !important;
            color: white !important;
        }

        [data-theme="dark"] .btn-calculate:hover {
            background: #3a0ca3 !important;
        }

        [data-theme="dark"] .calculator-result {
            background: #3a3a3a !important;
            border-color: #404040 !important;
        }

        [data-theme="dark"] .result-label {
            color: #b0b0b0 !important;
        }

        [data-theme="dark"] .result-value {
            color: #4cc9f0 !important;
        }

        [data-theme="dark"] .about-features li {
            color: #e0e0e0 !important;
        }

        [data-theme="dark"] .section-title {
            color: #e0e0e0 !important;
        }

        .tabs {
            display: flex;
            list-style: none;
            flex-wrap: wrap;
        }

        .tab {
            padding: 15px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-light);
            position: relative;
        }

        .tab:hover {
            color: var(--primary);
            background: rgba(67, 97, 238, 0.05);
        }

        .tab.active {
            color: var(--primary);
            border-bottom: 3px solid var(--primary);
            font-weight: 600;
        }

        .tab.active::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-light);
            border-radius: 0 0 3px 3px;
        }

        .tab-link {
            text-decoration: none;
            color: inherit;
            display: flex;
            align-items: center;
            gap: 8px;
            width: 100%;
            height: 100%;
        }

        .tab-link:hover {
            text-decoration: none;
            color: inherit;
        }

        .main-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .welcome-section {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: var(--shadow);
            text-align: center;
            margin-bottom: 30px;
            border-left: 5px solid var(--accent);
            position: relative;
            overflow: hidden;
        }

        .welcome-section::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 200px;
            height: 200px;
            background: var(--gradient-light);
            opacity: 0.05;
            border-radius: 50%;
            transform: translate(30%, -30%);
        }

        .welcome-section h2 {
            color: var(--dark);
            margin-bottom: 20px;
            font-size: 32px;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .welcome-section p {
            font-size: 18px;
            color: var(--text-light);
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
        }

        .calculator-section {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: var(--shadow);
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
        }

        .calculator-section::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: var(--gradient);
        }

        .section-title {
            color: var(--dark);
            margin-bottom: 25px;
            font-size: 28px;
            text-align: center;
            position: relative;
            display: inline-block;
            left: 50%;
            transform: translateX(-50%);
        }

        .section-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 100%;
            height: 4px;
            background: var(--gradient);
            border-radius: 2px;
        }

        .calculator-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--dark);
            font-weight: 600;
        }

        .form-control {
            width: 100%;
            padding: 12px 15px;
            background: var(--bg-light);
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            color: var(--text-dark);
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
        }

        .calculator-result {
            background: var(--gradient-light);
            padding: 25px;
            border-radius: 12px;
            margin-top: 20px;
            color: white;
            box-shadow: var(--shadow);
        }

        .result-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }

        .result-item:last-child {
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }

        .result-label {
            color: rgba(255, 255, 255, 0.9);
        }

        .result-value {
            color: white;
            font-weight: bold;
            font-size: 18px;
        }

        .btn-calculate {
            background: var(--gradient);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
            width: 100%;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }

        .btn-calculate::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: 0.5s;
        }

        .btn-calculate:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
        }

        .btn-calculate:hover::before {
            left: 100%;
        }

        .about-section {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: var(--shadow);
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
        }

        .about-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: var(--gradient);
        }

        .about-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        .about-text {
            line-height: 1.7;
            color: var(--text-light);
        }

        .about-text p {
            margin-bottom: 15px;
        }

        .about-features {
            list-style: none;
        }

        .about-features li {
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
        }

        .about-features li:hover {
            background: rgba(67, 97, 238, 0.05);
            padding-left: 10px;
            border-radius: 8px;
        }

        .about-features li:last-child {
            border-bottom: none;
        }

        .feature-icon {
            color: var(--success);
            font-weight: bold;
            font-size: 18px;
        }

        @media (max-width: 1024px) {
            .tabs {
                overflow-x: auto;
                flex-wrap: nowrap;
            }

            .tab {
                white-space: nowrap;
                padding: 15px;
            }

            .calculator-form, .about-content {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
                text-align: center;
                padding: 15px;
            }

            .logo-container {
                justify-content: center;
            }

            .company-contacts {
                flex-direction: column;
                gap: 5px;
            }

            .user-info {
                flex-direction: column;
                gap: 10px;
            }

            .navigation {
                padding: 0 15px;
            }

            .welcome-section, .calculator-section, .about-section {
                padding: 25px;
            }

            .welcome-section h2 {
                font-size: 24px;
            }

            .welcome-section p {
                font-size: 16px;
            }
        }

        @media (max-width: 480px) {
            .header {
                padding: 15px;
            }

            .navigation {
                padding: 0 15px;
            }

            .tab {
                padding: 12px;
                font-size: 14px;
            }

            .main-content {
                padding: 0 15px;
            }

            .calculator-section, .about-section {
                padding: 20px;
            }

            .section-title {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-container">
            <div class="logo">IT</div>
            <div class="company-info">
                <h1>ТехноИнновации</h1>
                <div class="company-contacts">
                    <div>📞 +7 (495) 123-45-67</div>
                    <div>✉️ info@technoinnovations.ru</div>
                </div>
            </div>
        </div>

        <div class="user-info">
            <div class="user-welcome">
                <div class="username">{% if user_full_name %}{{ user_full_name }}{% else %}{{ user.username }}{% endif %}</div>
                <div class="role">{% if user_role %}{{ user_role }}{% else %}Пользователь{% endif %}</div>
            </div>
            <button id="theme-toggle-btn" class="btn" style="margin-right: 10px;" title="Переключить тему">
                <i class="fas fa-moon"></i>
                <span id="theme-toggle-text">Темная тема</span>
            </button>
            <a href="/logout/" class="btn btn-logout">Выйти</a>
        </div>
    </div>

    <div class="navigation">
        <ul class="tabs">
            <li class="tab active">
                <span class="tab-link">
                    <span>Главная</span>
                </span>
            </li>
            <li class="tab">
                <a href="{% url 'workspace:workspace_dashboard' 1 %}" class="tab-link">
                    <span>Рабочая область</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'customers:customer_list' %}" class="tab-link">
                    <span>Реестр заказчиков</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'contractors:contractors_list' %}" class="tab-link">
                    <span>Реестр Исполнителей</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'equipment:list' %}" class="tab-link">
                    <span>Реестр оборудования</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'employees:employee_list' %}" class="tab-link">
                    <span>Реестр сотрудников</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'subcontractors:list' %}" class="tab-link">
                    <span>Реестр Субподрядчиков</span>
                </a>
            </li>
            <li class="tab">
                <a href="/staff/users/" class="tab-link">
                    <span>Создание пользователей</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'workspace_control:workspace_list' %}" class="tab-link">
                    <span>Создание рабочей области</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'projects:project_list' %}" class="tab-link">
                    <span>Управление проектом</span>
                </a>
            </li>
            <li class="tab">
                <a href="/commercial/" class="tab-link">
                    <span>Форма коммерческого предложения</span>
                </a>
            </li>
            <li class="tab">
                <a href="/nma/" class="tab-link">
                    <span>Форма стоимости НМА</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'itcost:dashboard' %}" class="tab-link">
                    <span>Система расчета стоимости</span>
                </a>
            </li>
        </ul>
    </div>

    <div class="main-content">
        <div class="welcome-section">
            <h2>Добро пожаловать в систему расчета стоимости IT-проектов</h2>
            <p>Комплексная платформа для управления проектами, расчета стоимости разработки,
            ведения реестров и формирования коммерческих предложений. Выберите нужный раздел
            в меню выше для начала работы.</p>
        </div>

        <div class="calculator-section">
            <h3 class="section-title">Рассчитайте стоимость и срок проекта</h3>
            <div class="calculator-form">
                <div>
                    <div class="form-group">
                        <label for="project-type">Тип проекта</label>
                        <select id="project-type" class="form-control">
                            <option value="">Выберите тип проекта</option>
                            <option value="website">Веб-сайт</option>
                            <option value="mobile">Мобильное приложение</option>
                            <option value="crm">CRM система</option>
                            <option value="erp">ERP система</option>
                            <option value="ecommerce">Интернет-магазин</option>
                            <option value="custom">Индивидуальная разработка</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="complexity">Сложность проекта</label>
                        <select id="complexity" class="form-control">
                            <option value="">Выберите сложность</option>
                            <option value="simple">Простой</option>
                            <option value="medium">Средний</option>
                            <option value="complex">Сложный</option>
                            <option value="very-complex">Очень сложный</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="team-size">Размер команды</label>
                        <select id="team-size" class="form-control">
                            <option value="">Выберите размер команды</option>
                            <option value="small">Малая (1-3 человека)</option>
                            <option value="medium">Средняя (4-6 человек)</option>
                            <option value="large">Большая (7-10 человек)</option>
                            <option value="xlarge">Очень большая (10+ человек)</option>
                        </select>
                    </div>
                </div>

                <div>
                    <div class="form-group">
                        <label for="timeline">Желаемые сроки (месяцы)</label>
                        <input type="number" id="timeline" class="form-control" min="1" max="24" placeholder="Введите количество месяцев">
                    </div>

                    <div class="form-group">
                        <label for="features">Количество основных функций</label>
                        <input type="number" id="features" class="form-control" min="1" max="50" placeholder="Введите количество функций">
                    </div>

                    <div class="form-group">
                        <label for="integrations">Количество интеграций</label>
                        <input type="number" id="integrations" class="form-control" min="0" max="20" placeholder="Введите количество интеграций">
                    </div>
                </div>
            </div>

            <button class="btn-calculate" id="calculate-btn">Рассчитать стоимость и сроки</button>

            <div class="calculator-result" id="result" style="display: none;">
                <div class="result-item">
                    <span class="result-label">Предварительная стоимость:</span>
                    <span class="result-value" id="cost-result">0 руб.</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Предполагаемые сроки:</span>
                    <span class="result-value" id="timeline-result">0 месяцев</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Рекомендуемая команда:</span>
                    <span class="result-value" id="team-result">0 человек</span>
                </div>
            </div>
        </div>

        <div class="about-section">
            <h3 class="section-title">О нашей компании</h3>
            <div class="about-content">
                <div class="about-text">
                    <p>Компания "ТехноИнновации" специализируется на разработке и внедрении IT-решений для бизнеса. Мы предлагаем полный цикл услуг: от анализа требований до поддержки готовых продуктов.</p>
                    <p>Наша команда состоит из опытных разработчиков, аналитиков и менеджеров проектов, готовых реализовать решения любой сложности.</p>
                    <p>Мы гордимся нашим подходом к работе, который сочетает в себе глубокое понимание бизнес-процессов и техническую экспертизу.</p>
                </div>
                <div class="about-features">
                    <li><span class="feature-icon">✓</span> Более 10 лет на рынке IT-услуг</li>
                    <li><span class="feature-icon">✓</span> Реализовано более 200 проектов</li>
                    <li><span class="feature-icon">✓</span> Команда из 50+ специалистов</li>
                    <li><span class="feature-icon">✓</span> Сертифицированные технологии</li>
                    <li><span class="feature-icon">✓</span> Поддержка 24/7</li>
                    <li><span class="feature-icon">✓</span> Гарантия качества</li>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const tabs = document.querySelectorAll('.tab');
            const currentPath = window.location.pathname;

            // Функция для определения активной вкладки на основе текущего URL
            function setActiveTab() {
                tabs.forEach(tab => {
                    const link = tab.querySelector('a');
                    if (link) {
                        const href = link.getAttribute('href');
                        // Проверяем, соответствует ли текущий URL ссылке вкладки
                        if (currentPath.includes(href) ||
                            (currentPath === '/' && link.href.includes('workspace_dashboard'))) {
                            tab.classList.add('active');
                        } else {
                            tab.classList.remove('active');
                        }
                    } else {
                        // Для вкладки "Главная" (без ссылки)
                        if (currentPath === '/' || currentPath === '/home/') {
                            tab.classList.add('active');
                        } else {
                            tab.classList.remove('active');
                        }
                    }
                });
            }

            // Устанавливаем активную вкладку при загрузке
            setActiveTab();

            // Обработчик клика по вкладкам
            tabs.forEach(tab => {
                tab.addEventListener('click', function(e) {
                    const link = this.querySelector('a');
                    if (link && !e.target.classList.contains('tab-link')) {
                        // Если клик был не по ссылке, переходим по ссылке
                        window.location.href = link.href;
                    }
                    // Если клик был по ссылке, стандартное поведение браузера сработает само
                });
            });

            // Имитация загрузки данных
            setTimeout(() => {
                const welcomeSection = document.querySelector('.welcome-section p');
                const userName = '{% if user_full_name %}{{ user_full_name }}{% else %}{{ user.username }}{% endif %}';
                welcomeSection.innerHTML = 'Добро пожаловать, <strong>' + userName + '</strong>!<br>Сегодня ' +
                    new Date().toLocaleDateString('ru-RU', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    }) + '. Готовы к работе?';
            }, 1000);

            // Калькулятор стоимости проекта
            const calculateBtn = document.getElementById('calculate-btn');
            const resultDiv = document.getElementById('result');

            calculateBtn.addEventListener('click', function() {
                // Получаем значения из формы
                const projectType = document.getElementById('project-type').value;
                const complexity = document.getElementById('complexity').value;
                const teamSize = document.getElementById('team-size').value;
                const timeline = parseInt(document.getElementById('timeline').value) || 0;
                const features = parseInt(document.getElementById('features').value) || 0;
                const integrations = parseInt(document.getElementById('integrations').value) || 0;

                // Проверяем, что все поля заполнены
                if (!projectType || !complexity || !teamSize || timeline === 0 || features === 0) {
                    alert('Пожалуйста, заполните все обязательные поля');
                    return;
                }

                // Базовая стоимость в зависимости от типа проекта
                let baseCost = 0;
                switch(projectType) {
                    case 'website': baseCost = 100000; break;
                    case 'mobile': baseCost = 150000; break;
                    case 'crm': baseCost = 300000; break;
                    case 'erp': baseCost = 500000; break;
                    case 'ecommerce': baseCost = 200000; break;
                    case 'custom': baseCost = 250000; break;
                }

                // Множитель сложности
                let complexityMultiplier = 1;
                switch(complexity) {
                    case 'simple': complexityMultiplier = 0.8; break;
                    case 'medium': complexityMultiplier = 1; break;
                    case 'complex': complexityMultiplier = 1.5; break;
                    case 'very-complex': complexityMultiplier = 2; break;
                }

                // Расчет стоимости
                let cost = baseCost * complexityMultiplier;
                cost += features * 15000; // Каждая функция добавляет стоимость
                cost += integrations * 25000; // Каждая интеграция добавляет стоимость

                // Расчет сроков
                let estimatedTimeline = Math.max(timeline, Math.ceil(features / 5) + Math.ceil(integrations / 2));
                if (complexity === 'complex') estimatedTimeline *= 1.2;
                if (complexity === 'very-complex') estimatedTimeline *= 1.5;

                // Расчет команды
                let recommendedTeam = 2; // Минимальная команда
                if (features > 10) recommendedTeam = 3;
                if (features > 20) recommendedTeam = 4;
                if (features > 30) recommendedTeam = 5;
                if (complexity === 'complex' || complexity === 'very-complex') recommendedTeam += 1;

                // Форматирование чисел
                const formattedCost = new Intl.NumberFormat('ru-RU').format(Math.round(cost));

                // Отображение результатов
                document.getElementById('cost-result').textContent = formattedCost + ' руб.';
                document.getElementById('timeline-result').textContent = Math.round(estimatedTimeline) + ' месяцев';
                document.getElementById('team-result').textContent = recommendedTeam + ' человек';

                // Показываем результаты
                resultDiv.style.display = 'block';

                // Анимация появления результатов
                resultDiv.style.opacity = '0';
                resultDiv.style.transform = 'translateY(20px)';
                resultDiv.style.display = 'block';

                setTimeout(() => {
                    resultDiv.style.transition = 'all 0.5s ease';
                    resultDiv.style.opacity = '1';
                    resultDiv.style.transform = 'translateY(0)';
                }, 10);
            });
        });

        // Предотвращаем изменение внешнего вида ссылок при наведении
        document.addEventListener('DOMContentLoaded', function() {
            const links = document.querySelectorAll('.tab-link');
            links.forEach(link => {
                link.addEventListener('mouseenter', function() {
                    this.style.color = 'inherit';
                    this.style.textDecoration = 'none';
                });
                link.addEventListener('mouseleave', function() {
                    this.style.color = 'inherit';
                    this.style.textDecoration = 'none';
                });
            });
        });
    </script>
    <script src="{% static 'js/theme-toggle.js' %}"></script>
</body>
</html>
```

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

def redirect_to_auth(request):
    return redirect('login:auth')

urlpatterns = [
    path('', redirect_to_auth),  # Перенаправление с корня на auth/
    path('admin/', admin.site.urls),
    path('', include('login.urls')),  # Включаем URLs из приложения main
    path('workspace/', include('workspace.urls')),
    path('customers/', include('customers.urls')),  # URL для приложения customers
    path('contractors/', include('contractors.urls')),  # URL для приложения customers
    path('equipment/', include('equipment.urls')),  # URL для приложения customers
    path('employees/', include('employees.urls')),  # URL для приложения customers
    path('subcontractors/', include('subcontractors.urls')),
    path('staff/', include('staff.urls')),
    path('workspace-control/', include('workspace_control.urls')),
    path('projects/', include('projects.urls')),
    path('commercial/', include('commercial_proposal.urls')),
    path('nma/', include('nmacost.urls')),
    path('itcost/', include('itcost.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

```python
"""
Django settings for ez project.

Generated by 'django-admin startproject' using Django 5.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w+!(#_tbe8^=jq8s@i#l7++rv&zb_$u(z$5i@4+#vc__-88&p*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition



INSTALLED_APPS = [
    'unfold',  # Django Unfold должен быть перед django.contrib.admin
    'unfold.contrib.filters',  # Дополнительные фильтры
    'login',
    'workspace',
    'customers',
    'contractors',
    'equipment',
    'employees',
    'subcontractors',
    'staff.apps.StaffConfig',
    'workspace_control',
    'projects',
    'commercial_proposal',
    'nmacost',
    'itcost',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Для поддержки локализации
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ez.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ← эта строка теперь будет работать
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ez.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/auth/'

# settings.py
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False

# Django Unfold settings
UNFOLD = {
    "SITE_TITLE": "EZ Project Admin",
    "SITE_HEADER": "Административная панель",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_LOGO": None,
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "ez.settings.environment_callback",
    "DASHBOARD_CALLBACK": None,
    "LOGIN": {
        "image": None,
        "redirect_after": None,
    },
    "STYLES": [],
    "SCRIPTS": [],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇳🇱",
                "ru": "🇷🇺",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Главное",
                "separator": True,
                "items": [
                    {
                        "title": "Проекты",
                        "link": "/admin/projects/project/",
                    },
                    {
                        "title": "Коммерческие предложения",
                        "link": "/admin/commercial_proposal/commercialproposal/",
                    },
                ],
            },
            {
                "title": "Контакты",
                "separator": True,
                "items": [
                    {
                        "title": "Заказчики",
                        "link": "/admin/customers/customer/",
                    },
                    {
                        "title": "Подрядчики",
                        "link": "/admin/contractors/contractor/",
                    },
                    {
                        "title": "Субподрядчики",
                        "link": "/admin/subcontractors/subcontractor/",
                    },
                    {
                        "title": "Сотрудники",
                        "link": "/admin/employees/employee/",
                    },
                ],
            },
            {
                "title": "Ресурсы",
                "separator": True,
                "items": [
                    {
                        "title": "Оборудование",
                        "link": "/admin/equipment/equipment/",
                    },
                    {
                        "title": "НМА",
                        "link": "/admin/nmacost/nmacost/",
                    },
                ],
            },
        ],
    },
    "TABS": [],
}

def environment_callback(request):
    """Callback функция для отображения окружения в админке"""
    if DEBUG:
        return "Разработка"
    return "Продакшн"
```

```python
"""
Django settings for ez project.

Generated by 'django-admin startproject' using Django 5.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w+!(#_tbe8^=jq8s@i#l7++rv&zb_$u(z$5i@4+#vc__-88&p*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition



INSTALLED_APPS = [
    'unfold',  # Django Unfold должен быть перед django.contrib.admin
    'unfold.contrib.filters',  # Дополнительные фильтры
    'login',
    'workspace',
    'customers',
    'contractors',
    'equipment',
    'employees',
    'subcontractors',
    'staff.apps.StaffConfig',
    'workspace_control',
    'projects',
    'commercial_proposal',
    'nmacost',
    'itcost',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Для поддержки локализации
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ez.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ← эта строка теперь будет работать
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ez.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/auth/'

# settings.py
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False

# Django Unfold settings
UNFOLD = {
    "SITE_TITLE": "EZ Project Admin",
    "SITE_HEADER": "Административная панель",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_LOGO": None,
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "ez.settings.environment_callback",
    "DASHBOARD_CALLBACK": None,
    "LOGIN": {
        "image": None,
        "redirect_after": None,
    },
    "STYLES": [],
    "SCRIPTS": [],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇳🇱",
                "ru": "🇷🇺",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Главное",
                "separator": True,
                "items": [
                    {
                        "title": "Проекты",
                        "link": "/admin/projects/project/",
                    },
                    {
                        "title": "Коммерческие предложения",
                        "link": "/admin/commercial_proposal/commercialproposal/",
                    },
                ],
            },
            {
                "title": "Контакты",
                "separator": True,
                "items": [
                    {
                        "title": "Заказчики",
                        "link": "/admin/customers/customer/",
                    },
                    {
                        "title": "Подрядчики",
                        "link": "/admin/contractors/contractor/",
                    },
                    {
                        "title": "Субподрядчики",
                        "link": "/admin/subcontractors/subcontractor/",
                    },
                    {
                        "title": "Сотрудники",
                        "link": "/admin/employees/employee/",
                    },
                ],
            },
            {
                "title": "Ресурсы",
                "separator": True,
                "items": [
                    {
                        "title": "Оборудование",
                        "link": "/admin/equipment/equipment/",
                    },
                    {
                        "title": "НМА",
                        "link": "/admin/nmacost/nmacost/",
                    },
                ],
            },
        ],
    },
    "TABS": [],
}

def environment_callback(request):
    """Callback функция для отображения окружения в админке"""
    if DEBUG:
        return "Разработка"
    return "Продакшн"
```

```plaintext
asgiref==3.9.1
Django==5.2.6
sqlparse==0.5.3
tzdata==2025.2
django-extensions
django-unfold

xhtml2pdf==0.2.10
reportlab<4.0.0
pandas>=2.2.0
openpyxl==3.1.2
python-docx==0.8.11
Pillow>=10.0.0
```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        return self.render_to_response({"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        return self.render_to_response({"form": form})


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
        return self.render_to_response({"form": form, "calculation": calculation})

    def post(self, request, *args, **kwargs):
        calculation = self.get_object()
        form = self.form_class(request.POST, instance=calculation)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            updated.save()
            messages.success(request, "Расчет обновлен.")
            return redirect("itcost:calculation_detail", pk=updated.pk)
        return self.render_to_response({"form": form, "calculation": calculation})


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

```

## Система расчета стоимости

- Добавлено приложение `itcost` с настройками компании, ролевой моделью и расчетом ключевых показателей (стоимость разработки, НМА и коммерческое предложение). Расчеты автоматически пересчитываются при сохранении и сохраняют расшифровку компонентов для детального просмотра.

```42:200:itcost/models.py
class CostCalculation(models.Model):
    """Расчет стоимости проекта с ключевыми показателями."""
    project_name = models.CharField(max_length=255, verbose_name="Название проекта")
    client_name = models.CharField(max_length=255, verbose_name="Заказчик", blank=True)
    project_brief = models.TextField(verbose_name="Описание/ТЗ", blank=True)
    estimated_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Трудоемкость, ч",
    )
    # ...
    commercial_offer_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость коммерческого предложения",
        editable=False,
    )
    # ---- расчетные методы ----
    def calculate_components(self) -> dict:
        base_labor = self.estimated_hours * self.hourly_rate
        # ...
        commercial_offer = development_cost * (
            Decimal("1") + self.commercial_markup_percent / Decimal("100")
        )
        return {
            "base_labor": base_labor,
            "management_overhead": management_overhead,
            # ...
        }
```

- Реализован дашборд, формы создания/редактирования расчетов, страница настроек и распределения ролей с защитой от дубликатов. Все маршруты подключены через `ez/urls.py`, а главная страница получила быструю ссылку на новую систему.

```21:155:itcost/views.py
class CostDashboardView(LoginRequiredMixin, ListView):
    """Сводный дашборд по расчетам и ролям."""
    model = CostCalculation
    template_name = "itcost/dashboard.html"
    # ...
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
            # ...
        }
        role_labels = dict(RoleAssignment.ROLE_CHOICES)
        role_summary = RoleAssignment.objects.values("role").annotate(
            total=Count("role")
        )
        context["role_breakdown"] = [
            {"label": role_labels.get(item["role"], item["role"]), "total": item["total"]}
            for item in role_summary
        ]
        return context
```

```10:29:ez/urls.py
urlpatterns = [
    path('', redirect_to_auth),
    path('admin/', admin.site.urls),
    # ...
    path('nma/', include('nmacost.urls')),
    path('itcost/', include('itcost.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

```722:735:login/templates/login/home.html
            <li class="tab">
                <a href="/nma/" class="tab-link">
                    <span>Форма стоимости НМА</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'itcost:dashboard' %}" class="tab-link">
                    <span>Система расчета стоимости</span>
                </a>
            </li>
```

- Добавлены шаблоны (`dashboard`, `cost_calculation_form/detail`, `organization_settings_form`, `role_assignment`), стилизованные формы, регистрация моделей в админке, медиа-настройки и зависимость `Pillow` для загрузки логотипа.

- Покрыты ключевые сценарии тестами (`python manage.py test itcost`).

## Что дальше
- Установить новую зависимость и применить миграции: `pip install -r requirements.txt` и `python manage.py migrate`.
- Загрузить логотипы/настроить роли через UI, затем создавать расчеты по адресу `/itcost/`.
- При необходимости добавить дополнительные проверки доступа (например, привязать роли к разрешениям).

```python
class CostCalculation(models.Model):
    """Расчет стоимости проекта с ключевыми показателями."""
    project_name = models.CharField(max_length=255, verbose_name="Название проекта")
    client_name = models.CharField(max_length=255, verbose_name="Заказчик", blank=True)
    project_brief = models.TextField(verbose_name="Описание/ТЗ", blank=True)
    estimated_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Трудоемкость, ч",
    )
    # ...
    commercial_offer_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость коммерческого предложения",
        editable=False,
    )
    # ---- расчетные методы ----
    def calculate_components(self) -> dict:
        base_labor = self.estimated_hours * self.hourly_rate
        # ...
        commercial_offer = development_cost * (
            Decimal("1") + self.commercial_markup_percent / Decimal("100")
        )
        return {
            "base_labor": base_labor,
            "management_overhead": management_overhead,
            # ...
        }
```

```python
class CostDashboardView(LoginRequiredMixin, ListView):
    """Сводный дашборд по расчетам и ролям."""
    model = CostCalculation
    template_name = "itcost/dashboard.html"
    # ...
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
            # ...
        }
        role_labels = dict(RoleAssignment.ROLE_CHOICES)
        role_summary = RoleAssignment.objects.values("role").annotate(
            total=Count("role")
        )
        context["role_breakdown"] = [
            {"label": role_labels.get(item["role"], item["role"]), "total": item["total"]}
            for item in role_summary
        ]
        return context
```

```python
urlpatterns = [
    path('', redirect_to_auth),
    path('admin/', admin.site.urls),
    # ...
    path('nma/', include('nmacost.urls')),
    path('itcost/', include('itcost.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

```html
            <li class="tab">
                <a href="/nma/" class="tab-link">
                    <span>Форма стоимости НМА</span>
                </a>
            </li>
            <li class="tab">
                <a href="{% url 'itcost:dashboard' %}" class="tab-link">
                    <span>Система расчета стоимости</span>
                </a>
            </li>
```

---

**User**

Внеси пару модификаций в приложение расчета стоимости проекта

При расчете стоимости стоит предлагать собирать информацию из раздела форма стоимости нма и из формы комерческого предложения

Также стоит сделать так чтобы система расчета стоимости была в таком же сайдбаре как и остальные приложения

Должен предоставляться выбор, выбрать уже созданную форму нма и комерческого предложения или создать ее с нуля, при создании с нуля должна вызываться форма создания из форм нма и комерческого предложения

---

**Cursor**

Изучаю структуру приложений НМА и коммерческого предложения, а также сайдбар, чтобы интегрировать их в систему расчета стоимости.


Создаю базовый шаблон с сайдбаром и модифицирую модель и формы для интеграции с НМА и коммерческими предложениями.


Создаю базовый шаблон с сайдбаром и обновляю модель для интеграции с НМА и коммерческими предложениями.


```html
{% extends 'base.html' %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <!-- Включаем боковую панель -->
        {% include 'itcost/includes/sidebar.html' %}

        <!-- Основное содержимое -->
        <div class="col-md-9 col-lg-10 ms-sm-auto px-4 py-4">
            {% block main_content %}
            <!-- Здесь будет основное содержимое страницы -->
            {% endblock %}
        </div>
    </div>
</div>
{% endblock %}

```

```html
{% load static %}
<!-- Боковая панель навигации -->
<div class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
    <div class="position-sticky pt-3">
        <div class="sidebar-logo text-center mb-4">
            <h6 class="text-muted">Система управления проектами</h6>
        </div>

        <ul class="nav flex-column">
            <li class="nav-item mb-3">
                <button id="theme-toggle-btn" class="nav-link w-100 text-start" type="button" style="border: none; background: none; cursor: pointer; padding: 0.75rem 1rem;">
                    <i class="fas fa-moon me-2"></i>
                    <span id="theme-toggle-text">Темная тема</span>
                </button>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if request.path == '/home/' %}active{% endif %}" href="/home/">
                    <i class="fas fa-home me-2"></i>
                    Главная
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'workspace' in request.path %}active{% endif %}" href="{% url 'workspace:workspace_dashboard' 1 %}">
                    <i class="fas fa-briefcase me-2"></i>
                    Рабочая область
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'customers' in request.path %}active{% endif %}" href="{% url 'customers:customer_list' %}">
                    <i class="fas fa-users me-2"></i>
                    Реестр заказчиков
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'contractors' in request.path %}active{% endif %}" href="{% url 'contractors:contractors_list' %}">
                    <i class="fas fa-user-tie me-2"></i>
                    Реестр Исполнителей
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'equipment' in request.path %}active{% endif %}" href="{% url 'equipment:list' %}">
                    <i class="fas fa-tools me-2"></i>
                    Реестр оборудования
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'employees' in request.path %}active{% endif %}" href="{% url 'employees:employee_list' %}">
                    <i class="fas fa-id-badge me-2"></i>
                    Реестр сотрудников
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'subcontractors' in request.path %}active{% endif %}" href="{% url 'subcontractors:list' %}">
                    <i class="fas fa-building me-2"></i>
                    Реестр Субподрядчиков
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'workspace_control' in request.path %}active{% endif %}" href="{% url 'workspace_control:workspace_list' %}">
                    <i class="fas fa-plus-circle me-2"></i>
                    Создание рабочей области
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'projects' in request.path %}active{% endif %}" href="{% url 'projects:project_list' %}">
                    <i class="fas fa-project-diagram me-2"></i>
                    Управление проектом
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if '/commercial/' in request.path %}active{% endif %}" href="/commercial/">
                    <i class="fas fa-file-contract me-2"></i>
                    Форма коммерческого предложения
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if '/nma/' in request.path %}active{% endif %}" href="/nma/">
                    <i class="fas fa-calculator me-2"></i>
                    Форма стоимости НМА
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'itcost' in request.path %}active{% endif %}" href="{% url 'itcost:dashboard' %}">
                    <i class="fas fa-calculator me-2"></i>
                    Система расчета стоимости
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if 'user_management' in request.path %}active{% endif %}" href="/staff/users/">
                    <i class="fas fa-user-plus me-2"></i>
                    Создание пользователей
                </a>
            </li>
        </ul>
    </div>
</div>

<style>
    .sidebar {
        min-height: calc(100vh - 56px);
        box-shadow: inset -1px 0 0 rgba(0, 0, 0, .1);
    }

    .nav-link {
        color: #333;
        padding: 0.75rem 1rem;
        border-left: 3px solid transparent;
        transition: all 0.2s;
    }

    .nav-link:hover {
        background-color: #f8f9fa;
        border-left: 3px solid #0d6efd;
        color: #0d6efd;
    }

    .nav-link.active {
        font-weight: 600;
        color: #0d6efd;
        background-color: #e9ecef;
        border-left: 3px solid #0d6efd;
    }

    .sidebar-logo {
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 1rem;
    }

    .nav-item {
        margin-bottom: 0.25rem;
    }

    .nav-link i {
        width: 20px;
        text-align: center;
    }

    #theme-toggle-btn {
        transition: all 0.2s;
    }

    #theme-toggle-btn:hover {
        background-color: #f8f9fa !important;
    }

    [data-theme="dark"] #theme-toggle-btn:hover {
        background-color: #3a3a3a !important;
    }
</style>

```

Добавляю связи с НМА и коммерческими предложениями в модель и обновляю формы и представления.


```python
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()
```

```python
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class OrganizationSettings(models.Model):
    """Глобальные настройки компании, влияющие на расчеты и документы."""

    company_name = models.CharField(
        max_length=255, verbose_name="Название компании", blank=True
    )
    director_full_name = models.CharField(
        max_length=255, verbose_name="ФИО руководителя", blank=True
    )
    director_position = models.CharField(
        max_length=255, verbose_name="Должность руководителя", blank=True
    )
    logo = models.ImageField(
        upload_to="organization_logos/",
        verbose_name="Логотип предприятия",
        blank=True,
        null=True,
    )
    contact_phone = models.CharField(
        max_length=32, verbose_name="Контактный телефон", blank=True
    )
    contact_email = models.EmailField(verbose_name="Контактный email", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Настройки организации"
        verbose_name_plural = "Настройки организации"

    def __str__(self) -> str:
        return self.company_name or "Настройки организации"


class CostCalculation(models.Model):
    """Расчет стоимости проекта с ключевыми показателями."""

    project_name = models.CharField(max_length=255, verbose_name="Название проекта")
    client_name = models.CharField(
        max_length=255, verbose_name="Заказчик", blank=True
    )
    project_brief = models.TextField(verbose_name="Описание/ТЗ", blank=True)
    estimated_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Трудоемкость, ч",
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Ставка, ₽/ч",
    )
    infrastructure_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Инфраструктурные затраты",
    )
    other_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Прочие расходы",
    )
    management_overhead_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("15.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Управленческие расходы, %",
    )
    risk_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Риск, %",
    )
    profit_margin_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("200.00")),
        ],
        verbose_name="Маржа прибыли, %",
    )
    asset_capitalization_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("80.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Доля капитализации НМА, %",
    )
    commercial_markup_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("300.00")),
        ],
        verbose_name="Наценка коммерческого предложения, %",
    )
    development_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость разработки проекта",
        editable=False,
    )
    intangible_asset_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость нематериального актива",
        editable=False,
    )
    commercial_offer_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Стоимость коммерческого предложения",
        editable=False,
    )
    # Связи с другими формами
    nma_cost = models.ForeignKey(
        'nmacost.NMACost',
        on_delete=models.SET_NULL,
        related_name="cost_calculations",
        verbose_name="Стоимость НМА",
        null=True,
        blank=True,
    )
    commercial_proposal = models.ForeignKey(
        'commercial_proposal.CommercialProposal',
        on_delete=models.SET_NULL,
        related_name="cost_calculations",
        verbose_name="Коммерческое предложение",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="cost_calculations",
        verbose_name="Инициатор",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Расчет стоимости"
        verbose_name_plural = "Расчеты стоимости"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.project_name} — {self.development_cost} ₽"

    # ---- расчетные методы ----
    def calculate_components(self) -> dict:
        base_labor = self.estimated_hours * self.hourly_rate
        management_overhead = base_labor * (
            self.management_overhead_percent / Decimal("100")
        )
        risk_reserve = base_labor * (self.risk_percent / Decimal("100"))
        profit_margin = base_labor * (self.profit_margin_percent / Decimal("100"))

        development_cost = (
            base_labor
            + management_overhead
            + risk_reserve
            + profit_margin
            + self.infrastructure_cost
            + self.other_expenses
        )
        intangible_asset = development_cost * (
            self.asset_capitalization_percent / Decimal("100")
        )
        commercial_offer = development_cost * (
            Decimal("1") + self.commercial_markup_percent / Decimal("100")
        )
        return {
            "base_labor": base_labor,
            "management_overhead": management_overhead,
            "risk_reserve": risk_reserve,
            "profit_margin": profit_margin,
            "development_cost": development_cost,
            "intangible_asset": intangible_asset,
            "commercial_offer": commercial_offer,
        }

    def save(self, *args, **kwargs):
        components = self.calculate_components()
        self.development_cost = components["development_cost"]
        self.intangible_asset_cost = components["intangible_asset"]
        self.commercial_offer_cost = components["commercial_offer"]
        super().save(*args, **kwargs)


class RoleAssignment(models.Model):
    """Привязка ролей участников системы к пользователям."""

    GLOBAL_ADMIN = "global_admin"
    COMMERCIAL_DIRECTOR = "commercial_director"
    ACCOUNTANT = "accountant"
    HR_SPECIALIST = "hr_specialist"

    ROLE_CHOICES = [
        (GLOBAL_ADMIN, "Глобальный администратор"),
        (COMMERCIAL_DIRECTOR, "Коммерческий директор"),
        (ACCOUNTANT, "Бухгалтер"),
        (HR_SPECIALIST, "Кадровик"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="itcost_roles"
    )
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_itcost_roles",
        verbose_name="Назначил",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Роль в системе расчета"
        verbose_name_plural = "Роли в системе расчета"
        unique_together = ("user", "role")
        ordering = ("-assigned_at",)

    def __str__(self) -> str:
        return f"{self.user} — {self.get_role_display()}"

```

Обновляю форму для выбора/создания НМА и коммерческих предложений:


```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
        }


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all() if HAS_NMA else None,
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all() if HAS_COMMERCIAL else None,
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

Обновляю views для обработки создания новых форм и обновляю шаблоны:


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        return self.render_to_response({"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        return self.render_to_response({"form": form})


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
        return self.render_to_response({"form": form, "calculation": calculation})

    def post(self, request, *args, **kwargs):
        calculation = self.get_object()
        form = self.form_class(request.POST, instance=calculation)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            updated.save()
            messages.success(request, "Расчет обновлен.")
            return redirect("itcost:calculation_detail", pk=updated.pk)
        return self.render_to_response({"form": form, "calculation": calculation})


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

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        form = self.form_class(request.POST)
        context = {"form": form}
        
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
                # Если форма НМА невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id:
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except:
                    pass
        
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
                # Если форма коммерческого предложения невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id:
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except:
                    pass
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            if nma_cost:
                calculation.nma_cost = nma_cost
            if commercial_proposal:
                calculation.commercial_proposal = commercial_proposal
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
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
        return self.render_to_response({"form": form, "calculation": calculation})

    def post(self, request, *args, **kwargs):
        calculation = self.get_object()
        form = self.form_class(request.POST, instance=calculation)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            updated.save()
            messages.success(request, "Расчет обновлен.")
            return redirect("itcost:calculation_detail", pk=updated.pk)
        return self.render_to_response({"form": form, "calculation": calculation})


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

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        form = self.form_class(request.POST)
        context = {"form": form}
        
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
                # Если форма НМА невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id:
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except:
                    pass
        
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
                # Если форма коммерческого предложения невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id:
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except:
                    pass
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            if nma_cost:
                calculation.nma_cost = nma_cost
            if commercial_proposal:
                calculation.commercial_proposal = commercial_proposal
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
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
            if nma_id:
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except:
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
            if commercial_id:
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except:
                    pass
        elif form.data.get("commercial_source") == "none":
            commercial_proposal = None
        
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            # Привязываем созданные или выбранные формы
            if nma_cost is not None:
                updated.nma_cost = nma_cost
            if commercial_proposal is not None:
                updated.commercial_proposal = commercial_proposal
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

```

Обновляю шаблон формы для интеграции с НМА и коммерческими предложениями:


```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block main_content %}
<div class="container-fluid py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" id="calculation-form">
                        {% csrf_token %}
                        
                        <!-- Основные поля расчета -->
                        <h6 class="mb-3">Основная информация</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.project_name.label }}{% if form.project_name.field.required %} *{% endif %}</label>
                                {{ form.project_name }}
                                {% for error in form.project_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.client_name.label }}{% if form.client_name.field.required %} *{% endif %}</label>
                                {{ form.client_name }}
                                {% for error in form.client_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-12">
                                <label class="form-label">{{ form.project_brief.label }}{% if form.project_brief.field.required %} *{% endif %}</label>
                                {{ form.project_brief }}
                                {% for error in form.project_brief.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Выбор источника данных НМА -->
                        <h6 class="mb-3">Источник данных НМА</h6>
                        <div class="mb-4">
                            {% for choice in form.nma_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.nma_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующей формы НМА -->
                            <div id="existing-nma-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_nma.label }}</label>
                                {{ form.existing_nma }}
                                {% for error in form.existing_nma.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            
                            <!-- Форма создания новой НМА -->
                            <div id="new-nma-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание новой формы НМА</h6>
                                        {% if nma_form %}
                                            {% for field in nma_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Выбор источника данных коммерческого предложения -->
                        <h6 class="mb-3">Источник данных коммерческого предложения</h6>
                        <div class="mb-4">
                            {% for choice in form.commercial_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.commercial_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующего коммерческого предложения -->
                            <div id="existing-commercial-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_commercial.label }}</label>
                                {{ form.existing_commercial }}
                                {% for error in form.existing_commercial.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            
                            <!-- Форма создания нового коммерческого предложения -->
                            <div id="new-commercial-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание нового коммерческого предложения</h6>
                                        {% if commercial_form %}
                                            {% for field in commercial_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                            
                                            {% if service_formset %}
                                                <h6 class="mt-4">Услуги</h6>
                                                {{ service_formset.management_form }}
                                                <div id="service-items">
                                                    {% for form_item in service_formset %}
                                                        <div class="service-item mb-3 p-3 border rounded">
                                                            {% for field in form_item %}
                                                                {% if not field.is_hidden %}
                                                                    <div class="mb-2">
                                                                        <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                                        {{ field }}
                                                                        {% for error in field.errors %}
                                                                            <div class="text-danger small">{{ error }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% else %}
                                                                    {{ field }}
                                                                {% endif %}
                                                            {% endfor %}
                                                        </div>
                                                    {% endfor %}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Параметры расчета -->
                        <h6 class="mb-3">Параметры расчета</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.estimated_hours.label }}{% if form.estimated_hours.field.required %} *{% endif %}</label>
                                {{ form.estimated_hours }}
                                {% for error in form.estimated_hours.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.hourly_rate.label }}{% if form.hourly_rate.field.required %} *{% endif %}</label>
                                {{ form.hourly_rate }}
                                {% for error in form.hourly_rate.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.infrastructure_cost.label }}{% if form.infrastructure_cost.field.required %} *{% endif %}</label>
                                {{ form.infrastructure_cost }}
                                {% for error in form.infrastructure_cost.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.other_expenses.label }}{% if form.other_expenses.field.required %} *{% endif %}</label>
                                {{ form.other_expenses }}
                                {% for error in form.other_expenses.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.management_overhead_percent.label }}{% if form.management_overhead_percent.field.required %} *{% endif %}</label>
                                {{ form.management_overhead_percent }}
                                {% for error in form.management_overhead_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.risk_percent.label }}{% if form.risk_percent.field.required %} *{% endif %}</label>
                                {{ form.risk_percent }}
                                {% for error in form.risk_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.profit_margin_percent.label }}{% if form.profit_margin_percent.field.required %} *{% endif %}</label>
                                {{ form.profit_margin_percent }}
                                {% for error in form.profit_margin_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.asset_capitalization_percent.label }}{% if form.asset_capitalization_percent.field.required %} *{% endif %}</label>
                                {{ form.asset_capitalization_percent }}
                                {% for error in form.asset_capitalization_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.commercial_markup_percent.label }}{% if form.commercial_markup_percent.field.required %} *{% endif %}</label>
                                {{ form.commercial_markup_percent }}
                                {% for error in form.commercial_markup_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Скрытые поля -->
                        {{ form.nma_cost }}
                        {{ form.commercial_proposal }}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора источника НМА
    const nmaSourceRadios = document.querySelectorAll('input[name="nma_source"]');
    const existingNmaSection = document.getElementById('existing-nma-section');
    const newNmaSection = document.getElementById('new-nma-section');
    
    function toggleNmaSections() {
        const selectedValue = document.querySelector('input[name="nma_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingNmaSection.style.display = 'block';
            newNmaSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'block';
        } else {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'none';
        }
    }
    
    nmaSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleNmaSections);
    });
    toggleNmaSections(); // Инициализация
    
    // Обработка выбора источника коммерческого предложения
    const commercialSourceRadios = document.querySelectorAll('input[name="commercial_source"]');
    const existingCommercialSection = document.getElementById('existing-commercial-section');
    const newCommercialSection = document.getElementById('new-commercial-section');
    
    function toggleCommercialSections() {
        const selectedValue = document.querySelector('input[name="commercial_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingCommercialSection.style.display = 'block';
            newCommercialSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'block';
        } else {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'none';
        }
    }
    
    commercialSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleCommercialSections);
    });
    toggleCommercialSections(); // Инициализация
});
</script>
{% endblock %}

```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}Дашборд расчета стоимости{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3">Система расчета стоимости IT-проекта</h1>
            <p class="text-muted mb-0">Контролируйте ключевые показатели стоимости разработки, НМА и коммерческих предложений.</p>
        </div>
        <div class="d-flex gap-2">
            <a class="btn btn-primary" href="{% url 'itcost:calculation_create' %}">
                <i class="fa-solid fa-plus me-2"></i>Новый расчет
            </a>
            <a class="btn btn-outline-secondary" href="{% url 'itcost:settings' %}">
                <i class="fa-solid fa-gear me-2"></i>Настройки
            </a>
            <a class="btn btn-outline-info" href="{% url 'itcost:roles' %}">
                <i class="fa-solid fa-users me-2"></i>Роли
            </a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Всего проектов</p>
                    <h3 class="fw-bold">{{ metrics.projects_count }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ metrics.development_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ metrics.intangible_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Коммерческие предложения</p>
                    <h3 class="fw-bold">{{ metrics.commercial_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Последние расчеты</h5>
                </div>
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead>
                            <tr>
                                <th>Проект</th>
                                <th>Заказчик</th>
                                <th>Разработка</th>
                                <th>НМА</th>
                                <th>Коммерческое</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for calc in calculations %}
                            <tr>
                                <td>
                                    <div class="fw-semibold">{{ calc.project_name }}</div>
                                    <small class="text-muted">обновлено {{ calc.updated_at|date:"d.m.Y H:i" }}</small>
                                </td>
                                <td>{{ calc.client_name|default:"—" }}</td>
                                <td>{{ calc.development_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.intangible_asset_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.commercial_offer_cost|floatformat:2 }} ₽</td>
                                <td class="text-end">
                                    <a href="{% url 'itcost:calculation_detail' calc.pk %}" class="btn btn-sm btn-outline-primary">Подробнее</a>
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="6" class="text-center py-4 text-muted">Пока нет расчетов. Создайте первый, чтобы увидеть аналитику.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Настройки компании</h5>
                </div>
                <div class="card-body">
                    {% if organization_settings %}
                        <p class="mb-1"><strong>{{ organization_settings.company_name|default:"Название не указано" }}</strong></p>
                        <p class="mb-1 text-muted">{{ organization_settings.director_full_name|default:"Руководитель не указан" }}</p>
                        <p class="mb-1">{{ organization_settings.director_position|default:"Должность не указана" }}</p>
                        <p class="mb-0">
                            <i class="fa-solid fa-phone me-2"></i>{{ organization_settings.contact_phone|default:"—" }}<br>
                            <i class="fa-solid fa-envelope me-2"></i>{{ organization_settings.contact_email|default:"—" }}
                        </p>
                    {% else %}
                        <p class="text-muted mb-0">Настройки еще не заполнены.</p>
                    {% endif %}
                </div>
            </div>

            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Ролевой состав</h5>
                </div>
                <div class="card-body">
                    {% for role in role_breakdown %}
                        <div class="d-flex justify-content-between mb-2">
                            <span>{{ role.label }}</span>
                            <span class="badge bg-primary rounded-pill">{{ role.total }}</span>
                        </div>
                    {% empty %}
                        <p class="text-muted mb-0">Роли еще не назначены.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}Дашборд расчета стоимости{% endblock %}

{% block main_content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3">Система расчета стоимости IT-проекта</h1>
            <p class="text-muted mb-0">Контролируйте ключевые показатели стоимости разработки, НМА и коммерческих предложений.</p>
        </div>
        <div class="d-flex gap-2">
            <a class="btn btn-primary" href="{% url 'itcost:calculation_create' %}">
                <i class="fa-solid fa-plus me-2"></i>Новый расчет
            </a>
            <a class="btn btn-outline-secondary" href="{% url 'itcost:settings' %}">
                <i class="fa-solid fa-gear me-2"></i>Настройки
            </a>
            <a class="btn btn-outline-info" href="{% url 'itcost:roles' %}">
                <i class="fa-solid fa-users me-2"></i>Роли
            </a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Всего проектов</p>
                    <h3 class="fw-bold">{{ metrics.projects_count }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ metrics.development_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ metrics.intangible_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Коммерческие предложения</p>
                    <h3 class="fw-bold">{{ metrics.commercial_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Последние расчеты</h5>
                </div>
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead>
                            <tr>
                                <th>Проект</th>
                                <th>Заказчик</th>
                                <th>Разработка</th>
                                <th>НМА</th>
                                <th>Коммерческое</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for calc in calculations %}
                            <tr>
                                <td>
                                    <div class="fw-semibold">{{ calc.project_name }}</div>
                                    <small class="text-muted">обновлено {{ calc.updated_at|date:"d.m.Y H:i" }}</small>
                                </td>
                                <td>{{ calc.client_name|default:"—" }}</td>
                                <td>{{ calc.development_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.intangible_asset_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.commercial_offer_cost|floatformat:2 }} ₽</td>
                                <td class="text-end">
                                    <a href="{% url 'itcost:calculation_detail' calc.pk %}" class="btn btn-sm btn-outline-primary">Подробнее</a>
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="6" class="text-center py-4 text-muted">Пока нет расчетов. Создайте первый, чтобы увидеть аналитику.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Настройки компании</h5>
                </div>
                <div class="card-body">
                    {% if organization_settings %}
                        <p class="mb-1"><strong>{{ organization_settings.company_name|default:"Название не указано" }}</strong></p>
                        <p class="mb-1 text-muted">{{ organization_settings.director_full_name|default:"Руководитель не указан" }}</p>
                        <p class="mb-1">{{ organization_settings.director_position|default:"Должность не указана" }}</p>
                        <p class="mb-0">
                            <i class="fa-solid fa-phone me-2"></i>{{ organization_settings.contact_phone|default:"—" }}<br>
                            <i class="fa-solid fa-envelope me-2"></i>{{ organization_settings.contact_email|default:"—" }}
                        </p>
                    {% else %}
                        <p class="text-muted mb-0">Настройки еще не заполнены.</p>
                    {% endif %}
                </div>
            </div>

            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Ролевой состав</h5>
                </div>
                <div class="card-body">
                    {% for role in role_breakdown %}
                        <div class="d-flex justify-content-between mb-2">
                            <span>{{ role.label }}</span>
                            <span class="badge bg-primary rounded-pill">{{ role.total }}</span>
                        </div>
                    {% empty %}
                        <p class="text-muted mb-0">Роли еще не назначены.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


```

Обновляю шаблон детального просмотра и другие шаблоны:


```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation.project_name }}{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3 mb-1">{{ calculation.project_name }}</h1>
            <p class="text-muted mb-0">{{ calculation.client_name|default:"Заказчик не указан" }}</p>
        </div>
        <div class="d-flex gap-2">
            <a href="{% url 'itcost:calculation_edit' calculation.pk %}" class="btn btn-outline-primary">
                <i class="fa-solid fa-pen me-2"></i>Редактировать
            </a>
            <a href="{% url 'itcost:dashboard' %}" class="btn btn-outline-secondary">К списку</a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ calculation.development_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ calculation.intangible_asset_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость коммерческого предложения</p>
                    <h3 class="fw-bold">{{ calculation.commercial_offer_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Входные данные</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <p class="text-muted mb-1">Трудоемкость</p>
                    <div>{{ calculation.estimated_hours }} ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Ставка</p>
                    <div>{{ calculation.hourly_rate }} ₽/ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Инфраструктурные затраты</p>
                    <div>{{ calculation.infrastructure_cost }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Прочие расходы</p>
                    <div>{{ calculation.other_expenses }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ calculation.management_overhead_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Риски</p>
                    <div>{{ calculation.risk_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Маржа</p>
                    <div>{{ calculation.profit_margin_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Капитализация НМА</p>
                    <div>{{ calculation.asset_capitalization_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Наценка КП</p>
                    <div>{{ calculation.commercial_markup_percent }}%</div>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Детализация расчетов</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-6">
                    <p class="text-muted mb-1">Базовая трудоемкость</p>
                    <div>{{ components.base_labor|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ components.management_overhead|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Риск-резерв</p>
                    <div>{{ components.risk_reserve|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Маржа прибыли</p>
                    <div>{{ components.profit_margin|floatformat:2 }} ₽</div>
                </div>
            </div>
            <hr>
            <p class="text-muted mb-1">Описание/ТЗ</p>
            <div>{{ calculation.project_brief|linebreaks|default:"—" }}</div>
        </div>
    </div>
</div>
{% endblock %}


```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation.project_name }}{% endblock %}

{% block main_content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3 mb-1">{{ calculation.project_name }}</h1>
            <p class="text-muted mb-0">{{ calculation.client_name|default:"Заказчик не указан" }}</p>
        </div>
        <div class="d-flex gap-2">
            <a href="{% url 'itcost:calculation_edit' calculation.pk %}" class="btn btn-outline-primary">
                <i class="fa-solid fa-pen me-2"></i>Редактировать
            </a>
            <a href="{% url 'itcost:dashboard' %}" class="btn btn-outline-secondary">К списку</a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ calculation.development_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ calculation.intangible_asset_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость коммерческого предложения</p>
                    <h3 class="fw-bold">{{ calculation.commercial_offer_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Входные данные</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <p class="text-muted mb-1">Трудоемкость</p>
                    <div>{{ calculation.estimated_hours }} ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Ставка</p>
                    <div>{{ calculation.hourly_rate }} ₽/ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Инфраструктурные затраты</p>
                    <div>{{ calculation.infrastructure_cost }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Прочие расходы</p>
                    <div>{{ calculation.other_expenses }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ calculation.management_overhead_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Риски</p>
                    <div>{{ calculation.risk_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Маржа</p>
                    <div>{{ calculation.profit_margin_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Капитализация НМА</p>
                    <div>{{ calculation.asset_capitalization_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Наценка КП</p>
                    <div>{{ calculation.commercial_markup_percent }}%</div>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Детализация расчетов</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-6">
                    <p class="text-muted mb-1">Базовая трудоемкость</p>
                    <div>{{ components.base_labor|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ components.management_overhead|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Риск-резерв</p>
                    <div>{{ components.risk_reserve|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Маржа прибыли</p>
                    <div>{{ components.profit_margin|floatformat:2 }} ₽</div>
                </div>
            </div>
            <hr>
            <p class="text-muted mb-1">Описание/ТЗ</p>
            <div>{{ calculation.project_brief|linebreaks|default:"—" }}</div>
        </div>
    </div>
</div>
{% endblock %}


```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation.project_name }}{% endblock %}

{% block main_content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3 mb-1">{{ calculation.project_name }}</h1>
            <p class="text-muted mb-0">{{ calculation.client_name|default:"Заказчик не указан" }}</p>
        </div>
        <div class="d-flex gap-2">
            <a href="{% url 'itcost:calculation_edit' calculation.pk %}" class="btn btn-outline-primary">
                <i class="fa-solid fa-pen me-2"></i>Редактировать
            </a>
            <a href="{% url 'itcost:dashboard' %}" class="btn btn-outline-secondary">К списку</a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ calculation.development_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ calculation.intangible_asset_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость коммерческого предложения</p>
                    <h3 class="fw-bold">{{ calculation.commercial_offer_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Входные данные</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <p class="text-muted mb-1">Трудоемкость</p>
                    <div>{{ calculation.estimated_hours }} ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Ставка</p>
                    <div>{{ calculation.hourly_rate }} ₽/ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Инфраструктурные затраты</p>
                    <div>{{ calculation.infrastructure_cost }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Прочие расходы</p>
                    <div>{{ calculation.other_expenses }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ calculation.management_overhead_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Риски</p>
                    <div>{{ calculation.risk_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Маржа</p>
                    <div>{{ calculation.profit_margin_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Капитализация НМА</p>
                    <div>{{ calculation.asset_capitalization_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Наценка КП</p>
                    <div>{{ calculation.commercial_markup_percent }}%</div>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Детализация расчетов</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-6">
                    <p class="text-muted mb-1">Базовая трудоемкость</p>
                    <div>{{ components.base_labor|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ components.management_overhead|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Риск-резерв</p>
                    <div>{{ components.risk_reserve|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Маржа прибыли</p>
                    <div>{{ components.profit_margin|floatformat:2 }} ₽</div>
                </div>
            </div>
            <hr>
            <p class="text-muted mb-1">Описание/ТЗ</p>
            <div>{{ calculation.project_brief|linebreaks|default:"—" }}</div>
        </div>
    </div>

    <!-- Информация о связанных формах -->
    {% if calculation.nma_cost %}
    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Связанная форма НМА</h5>
        </div>
        <div class="card-body">
            <p><strong>Проект:</strong> {{ calculation.nma_cost.project_name }}</p>
            <p><strong>Срок разработки:</strong> {{ calculation.nma_cost.development_period }}</p>
            <p><strong>Итоговая стоимость:</strong> {{ calculation.nma_cost.total_cost|floatformat:2 }} ₽</p>
            <a href="{% url 'nmacost:nmacost-detail' calculation.nma_cost.id %}" class="btn btn-sm btn-outline-primary">
                Открыть форму НМА
            </a>
        </div>
    </div>
    {% endif %}

    {% if calculation.commercial_proposal %}
    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Связанное коммерческое предложение</h5>
        </div>
        <div class="card-body">
            <p><strong>Название:</strong> {{ calculation.commercial_proposal.title }}</p>
            <p><strong>Заказчик:</strong> {{ calculation.commercial_proposal.customer.name }}</p>
            <p><strong>Итоговая стоимость:</strong> {{ calculation.commercial_proposal.total_cost|floatformat:2 }} ₽</p>
            <a href="{% url 'commercial_proposal:proposal_detail' calculation.commercial_proposal.pk %}" class="btn btn-sm btn-outline-primary">
                Открыть коммерческое предложение
            </a>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}


```

Обновляю оставшиеся шаблоны для использования базового шаблона с сайдбаром:


```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}Настройки организации{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Основные настройки системы</h5>
                    <small class="text-muted">Данные используются в расчетах и документах.</small>
                </div>
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data">
                        {% csrf_token %}
                        {% for field in form %}
                            <div class="mb-3">
                                <label class="form-label">{{ field.label }}</label>
                                {{ field }}
                                {% for error in field.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        {% endfor %}
                        <div class="d-flex justify-content-between">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Назад</a>
                            <button type="submit" class="btn btn-primary">Сохранить</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}Настройки организации{% endblock %}

{% block main_content %}
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Основные настройки системы</h5>
                    <small class="text-muted">Данные используются в расчетах и документах.</small>
                </div>
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data">
                        {% csrf_token %}
                        {% for field in form %}
                            <div class="mb-3">
                                <label class="form-label">{{ field.label }}</label>
                                {{ field }}
                                {% for error in field.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        {% endfor %}
                        <div class="d-flex justify-content-between">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Назад</a>
                            <button type="submit" class="btn btn-primary">Сохранить</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}Роли участников{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row g-4">
        <div class="col-lg-5">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Назначить роль</h5>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {% for field in form %}
                            <div class="mb-3">
                                <label class="form-label">{{ field.label }}</label>
                                {{ field }}
                                {% for error in field.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        {% endfor %}
                        <button type="submit" class="btn btn-primary w-100">Назначить</button>
                    </form>
                </div>
            </div>
        </div>
        <div class="col-lg-7">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0 d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Актуальные назначения</h5>
                    <a href="{% url 'itcost:dashboard' %}" class="btn btn-sm btn-outline-secondary">К дашборду</a>
                </div>
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead>
                            <tr>
                                <th>Пользователь</th>
                                <th>Роль</th>
                                <th>Назначил</th>
                                <th>Когда</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for assignment in assignments %}
                            <tr>
                                <td>{{ assignment.user.get_full_name|default:assignment.user.username }}</td>
                                <td>{{ assignment.get_role_display }}</td>
                                <td>{{ assignment.assigned_by.get_full_name|default:assignment.assigned_by }}</td>
                                <td>{{ assignment.assigned_at|date:"d.m.Y H:i" }}</td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="4" class="text-center text-muted py-4">Роли еще не распределены.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}Роли участников{% endblock %}

{% block main_content %}
<div class="container py-4">
    <div class="row g-4">
        <div class="col-lg-5">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Назначить роль</h5>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {% for field in form %}
                            <div class="mb-3">
                                <label class="form-label">{{ field.label }}</label>
                                {{ field }}
                                {% for error in field.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        {% endfor %}
                        <button type="submit" class="btn btn-primary w-100">Назначить</button>
                    </form>
                </div>
            </div>
        </div>
        <div class="col-lg-7">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0 d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Актуальные назначения</h5>
                    <a href="{% url 'itcost:dashboard' %}" class="btn btn-sm btn-outline-secondary">К дашборду</a>
                </div>
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead>
                            <tr>
                                <th>Пользователь</th>
                                <th>Роль</th>
                                <th>Назначил</th>
                                <th>Когда</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for assignment in assignments %}
                            <tr>
                                <td>{{ assignment.user.get_full_name|default:assignment.user.username }}</td>
                                <td>{{ assignment.get_role_display }}</td>
                                <td>{{ assignment.assigned_by.get_full_name|default:assignment.assigned_by }}</td>
                                <td>{{ assignment.assigned_at|date:"d.m.Y H:i" }}</td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="4" class="text-center text-muted py-4">Роли еще не распределены.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


```

Проверяю и исправляю обработку форм в views:


Исправляю обработку формы в views для корректной работы с radio buttons:


```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if HAS_NMA else forms.ModelChoiceField.empty_queryset,
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all() if HAS_COMMERCIAL else None,
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if HAS_NMA else forms.ModelChoiceField.empty_queryset,
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if HAS_COMMERCIAL else forms.ModelChoiceField.empty_queryset,
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if HAS_NMA else forms.ModelChoiceField.empty_queryset,
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if HAS_COMMERCIAL else forms.ModelChoiceField.empty_queryset,
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

Обновляю шаблон формы, чтобы скрывать недоступные опции:


```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block main_content %}
<div class="container-fluid py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" id="calculation-form">
                        {% csrf_token %}
                        
                        <!-- Основные поля расчета -->
                        <h6 class="mb-3">Основная информация</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.project_name.label }}{% if form.project_name.field.required %} *{% endif %}</label>
                                {{ form.project_name }}
                                {% for error in form.project_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.client_name.label }}{% if form.client_name.field.required %} *{% endif %}</label>
                                {{ form.client_name }}
                                {% for error in form.client_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-12">
                                <label class="form-label">{{ form.project_brief.label }}{% if form.project_brief.field.required %} *{% endif %}</label>
                                {{ form.project_brief }}
                                {% for error in form.project_brief.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Выбор источника данных НМА -->
                        {% if form.nma_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных НМА</h6>
                        <div class="mb-4">
                            {% for choice in form.nma_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.nma_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующей формы НМА -->
                            <div id="existing-nma-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_nma.label }}</label>
                                {{ form.existing_nma }}
                                {% for error in form.existing_nma.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            
                            <!-- Форма создания новой НМА -->
                            <div id="new-nma-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание новой формы НМА</h6>
                                        {% if nma_form %}
                                            {% for field in nma_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Выбор источника данных коммерческого предложения -->
                        <h6 class="mb-3">Источник данных коммерческого предложения</h6>
                        <div class="mb-4">
                            {% for choice in form.commercial_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.commercial_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующего коммерческого предложения -->
                            <div id="existing-commercial-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_commercial.label }}</label>
                                {{ form.existing_commercial }}
                                {% for error in form.existing_commercial.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            
                            <!-- Форма создания нового коммерческого предложения -->
                            <div id="new-commercial-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание нового коммерческого предложения</h6>
                                        {% if commercial_form %}
                                            {% for field in commercial_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                            
                                            {% if service_formset %}
                                                <h6 class="mt-4">Услуги</h6>
                                                {{ service_formset.management_form }}
                                                <div id="service-items">
                                                    {% for form_item in service_formset %}
                                                        <div class="service-item mb-3 p-3 border rounded">
                                                            {% for field in form_item %}
                                                                {% if not field.is_hidden %}
                                                                    <div class="mb-2">
                                                                        <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                                        {{ field }}
                                                                        {% for error in field.errors %}
                                                                            <div class="text-danger small">{{ error }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% else %}
                                                                    {{ field }}
                                                                {% endif %}
                                                            {% endfor %}
                                                        </div>
                                                    {% endfor %}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Параметры расчета -->
                        <h6 class="mb-3">Параметры расчета</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.estimated_hours.label }}{% if form.estimated_hours.field.required %} *{% endif %}</label>
                                {{ form.estimated_hours }}
                                {% for error in form.estimated_hours.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.hourly_rate.label }}{% if form.hourly_rate.field.required %} *{% endif %}</label>
                                {{ form.hourly_rate }}
                                {% for error in form.hourly_rate.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.infrastructure_cost.label }}{% if form.infrastructure_cost.field.required %} *{% endif %}</label>
                                {{ form.infrastructure_cost }}
                                {% for error in form.infrastructure_cost.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.other_expenses.label }}{% if form.other_expenses.field.required %} *{% endif %}</label>
                                {{ form.other_expenses }}
                                {% for error in form.other_expenses.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.management_overhead_percent.label }}{% if form.management_overhead_percent.field.required %} *{% endif %}</label>
                                {{ form.management_overhead_percent }}
                                {% for error in form.management_overhead_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.risk_percent.label }}{% if form.risk_percent.field.required %} *{% endif %}</label>
                                {{ form.risk_percent }}
                                {% for error in form.risk_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.profit_margin_percent.label }}{% if form.profit_margin_percent.field.required %} *{% endif %}</label>
                                {{ form.profit_margin_percent }}
                                {% for error in form.profit_margin_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.asset_capitalization_percent.label }}{% if form.asset_capitalization_percent.field.required %} *{% endif %}</label>
                                {{ form.asset_capitalization_percent }}
                                {% for error in form.asset_capitalization_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.commercial_markup_percent.label }}{% if form.commercial_markup_percent.field.required %} *{% endif %}</label>
                                {{ form.commercial_markup_percent }}
                                {% for error in form.commercial_markup_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Скрытые поля -->
                        {{ form.nma_cost }}
                        {{ form.commercial_proposal }}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора источника НМА
    const nmaSourceRadios = document.querySelectorAll('input[name="nma_source"]');
    const existingNmaSection = document.getElementById('existing-nma-section');
    const newNmaSection = document.getElementById('new-nma-section');
    
    function toggleNmaSections() {
        const selectedValue = document.querySelector('input[name="nma_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingNmaSection.style.display = 'block';
            newNmaSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'block';
        } else {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'none';
        }
    }
    
    nmaSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleNmaSections);
    });
    toggleNmaSections(); // Инициализация
    
    // Обработка выбора источника коммерческого предложения
    const commercialSourceRadios = document.querySelectorAll('input[name="commercial_source"]');
    const existingCommercialSection = document.getElementById('existing-commercial-section');
    const newCommercialSection = document.getElementById('new-commercial-section');
    
    function toggleCommercialSections() {
        const selectedValue = document.querySelector('input[name="commercial_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingCommercialSection.style.display = 'block';
            newCommercialSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'block';
        } else {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'none';
        }
    }
    
    commercialSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleCommercialSections);
    });
    toggleCommercialSections(); // Инициализация
});
</script>
{% endblock %}

```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block main_content %}
<div class="container-fluid py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" id="calculation-form">
                        {% csrf_token %}
                        
                        <!-- Основные поля расчета -->
                        <h6 class="mb-3">Основная информация</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.project_name.label }}{% if form.project_name.field.required %} *{% endif %}</label>
                                {{ form.project_name }}
                                {% for error in form.project_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.client_name.label }}{% if form.client_name.field.required %} *{% endif %}</label>
                                {{ form.client_name }}
                                {% for error in form.client_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-12">
                                <label class="form-label">{{ form.project_brief.label }}{% if form.project_brief.field.required %} *{% endif %}</label>
                                {{ form.project_brief }}
                                {% for error in form.project_brief.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Выбор источника данных НМА -->
                        {% if form.nma_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных НМА</h6>
                        <div class="mb-4">
                            {% for choice in form.nma_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.nma_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующей формы НМА -->
                            {% if form.existing_nma.field.widget.input_type != 'hidden' %}
                            <div id="existing-nma-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_nma.label }}</label>
                                {{ form.existing_nma }}
                                {% for error in form.existing_nma.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания новой НМА -->
                            <div id="new-nma-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание новой формы НМА</h6>
                                        {% if nma_form %}
                                            {% for field in nma_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Выбор источника данных коммерческого предложения -->
                        <h6 class="mb-3">Источник данных коммерческого предложения</h6>
                        <div class="mb-4">
                            {% for choice in form.commercial_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.commercial_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующего коммерческого предложения -->
                            <div id="existing-commercial-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_commercial.label }}</label>
                                {{ form.existing_commercial }}
                                {% for error in form.existing_commercial.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            
                            <!-- Форма создания нового коммерческого предложения -->
                            <div id="new-commercial-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание нового коммерческого предложения</h6>
                                        {% if commercial_form %}
                                            {% for field in commercial_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                            
                                            {% if service_formset %}
                                                <h6 class="mt-4">Услуги</h6>
                                                {{ service_formset.management_form }}
                                                <div id="service-items">
                                                    {% for form_item in service_formset %}
                                                        <div class="service-item mb-3 p-3 border rounded">
                                                            {% for field in form_item %}
                                                                {% if not field.is_hidden %}
                                                                    <div class="mb-2">
                                                                        <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                                        {{ field }}
                                                                        {% for error in field.errors %}
                                                                            <div class="text-danger small">{{ error }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% else %}
                                                                    {{ field }}
                                                                {% endif %}
                                                            {% endfor %}
                                                        </div>
                                                    {% endfor %}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Параметры расчета -->
                        <h6 class="mb-3">Параметры расчета</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.estimated_hours.label }}{% if form.estimated_hours.field.required %} *{% endif %}</label>
                                {{ form.estimated_hours }}
                                {% for error in form.estimated_hours.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.hourly_rate.label }}{% if form.hourly_rate.field.required %} *{% endif %}</label>
                                {{ form.hourly_rate }}
                                {% for error in form.hourly_rate.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.infrastructure_cost.label }}{% if form.infrastructure_cost.field.required %} *{% endif %}</label>
                                {{ form.infrastructure_cost }}
                                {% for error in form.infrastructure_cost.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.other_expenses.label }}{% if form.other_expenses.field.required %} *{% endif %}</label>
                                {{ form.other_expenses }}
                                {% for error in form.other_expenses.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.management_overhead_percent.label }}{% if form.management_overhead_percent.field.required %} *{% endif %}</label>
                                {{ form.management_overhead_percent }}
                                {% for error in form.management_overhead_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.risk_percent.label }}{% if form.risk_percent.field.required %} *{% endif %}</label>
                                {{ form.risk_percent }}
                                {% for error in form.risk_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.profit_margin_percent.label }}{% if form.profit_margin_percent.field.required %} *{% endif %}</label>
                                {{ form.profit_margin_percent }}
                                {% for error in form.profit_margin_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.asset_capitalization_percent.label }}{% if form.asset_capitalization_percent.field.required %} *{% endif %}</label>
                                {{ form.asset_capitalization_percent }}
                                {% for error in form.asset_capitalization_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.commercial_markup_percent.label }}{% if form.commercial_markup_percent.field.required %} *{% endif %}</label>
                                {{ form.commercial_markup_percent }}
                                {% for error in form.commercial_markup_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Скрытые поля -->
                        {{ form.nma_cost }}
                        {{ form.commercial_proposal }}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора источника НМА
    const nmaSourceRadios = document.querySelectorAll('input[name="nma_source"]');
    const existingNmaSection = document.getElementById('existing-nma-section');
    const newNmaSection = document.getElementById('new-nma-section');
    
    function toggleNmaSections() {
        const selectedValue = document.querySelector('input[name="nma_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingNmaSection.style.display = 'block';
            newNmaSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'block';
        } else {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'none';
        }
    }
    
    nmaSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleNmaSections);
    });
    toggleNmaSections(); // Инициализация
    
    // Обработка выбора источника коммерческого предложения
    const commercialSourceRadios = document.querySelectorAll('input[name="commercial_source"]');
    const existingCommercialSection = document.getElementById('existing-commercial-section');
    const newCommercialSection = document.getElementById('new-commercial-section');
    
    function toggleCommercialSections() {
        const selectedValue = document.querySelector('input[name="commercial_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingCommercialSection.style.display = 'block';
            newCommercialSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'block';
        } else {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'none';
        }
    }
    
    commercialSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleCommercialSections);
    });
    toggleCommercialSections(); // Инициализация
});
</script>
{% endblock %}

```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block main_content %}
<div class="container-fluid py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" id="calculation-form">
                        {% csrf_token %}
                        
                        <!-- Основные поля расчета -->
                        <h6 class="mb-3">Основная информация</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.project_name.label }}{% if form.project_name.field.required %} *{% endif %}</label>
                                {{ form.project_name }}
                                {% for error in form.project_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.client_name.label }}{% if form.client_name.field.required %} *{% endif %}</label>
                                {{ form.client_name }}
                                {% for error in form.client_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-12">
                                <label class="form-label">{{ form.project_brief.label }}{% if form.project_brief.field.required %} *{% endif %}</label>
                                {{ form.project_brief }}
                                {% for error in form.project_brief.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Выбор источника данных НМА -->
                        {% if form.nma_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных НМА</h6>
                        <div class="mb-4">
                            {% for choice in form.nma_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.nma_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующей формы НМА -->
                            {% if form.existing_nma.field.widget.input_type != 'hidden' %}
                            <div id="existing-nma-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_nma.label }}</label>
                                {{ form.existing_nma }}
                                {% for error in form.existing_nma.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания новой НМА -->
                            <div id="new-nma-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание новой формы НМА</h6>
                                        {% if nma_form %}
                                            {% for field in nma_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Выбор источника данных коммерческого предложения -->
                        {% if form.commercial_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных коммерческого предложения</h6>
                        <div class="mb-4">
                            {% for choice in form.commercial_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.commercial_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующего коммерческого предложения -->
                            <div id="existing-commercial-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_commercial.label }}</label>
                                {{ form.existing_commercial }}
                                {% for error in form.existing_commercial.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            
                            <!-- Форма создания нового коммерческого предложения -->
                            <div id="new-commercial-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание нового коммерческого предложения</h6>
                                        {% if commercial_form %}
                                            {% for field in commercial_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                            
                                            {% if service_formset %}
                                                <h6 class="mt-4">Услуги</h6>
                                                {{ service_formset.management_form }}
                                                <div id="service-items">
                                                    {% for form_item in service_formset %}
                                                        <div class="service-item mb-3 p-3 border rounded">
                                                            {% for field in form_item %}
                                                                {% if not field.is_hidden %}
                                                                    <div class="mb-2">
                                                                        <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                                        {{ field }}
                                                                        {% for error in field.errors %}
                                                                            <div class="text-danger small">{{ error }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% else %}
                                                                    {{ field }}
                                                                {% endif %}
                                                            {% endfor %}
                                                        </div>
                                                    {% endfor %}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Параметры расчета -->
                        <h6 class="mb-3">Параметры расчета</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.estimated_hours.label }}{% if form.estimated_hours.field.required %} *{% endif %}</label>
                                {{ form.estimated_hours }}
                                {% for error in form.estimated_hours.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.hourly_rate.label }}{% if form.hourly_rate.field.required %} *{% endif %}</label>
                                {{ form.hourly_rate }}
                                {% for error in form.hourly_rate.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.infrastructure_cost.label }}{% if form.infrastructure_cost.field.required %} *{% endif %}</label>
                                {{ form.infrastructure_cost }}
                                {% for error in form.infrastructure_cost.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.other_expenses.label }}{% if form.other_expenses.field.required %} *{% endif %}</label>
                                {{ form.other_expenses }}
                                {% for error in form.other_expenses.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.management_overhead_percent.label }}{% if form.management_overhead_percent.field.required %} *{% endif %}</label>
                                {{ form.management_overhead_percent }}
                                {% for error in form.management_overhead_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.risk_percent.label }}{% if form.risk_percent.field.required %} *{% endif %}</label>
                                {{ form.risk_percent }}
                                {% for error in form.risk_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.profit_margin_percent.label }}{% if form.profit_margin_percent.field.required %} *{% endif %}</label>
                                {{ form.profit_margin_percent }}
                                {% for error in form.profit_margin_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.asset_capitalization_percent.label }}{% if form.asset_capitalization_percent.field.required %} *{% endif %}</label>
                                {{ form.asset_capitalization_percent }}
                                {% for error in form.asset_capitalization_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.commercial_markup_percent.label }}{% if form.commercial_markup_percent.field.required %} *{% endif %}</label>
                                {{ form.commercial_markup_percent }}
                                {% for error in form.commercial_markup_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Скрытые поля -->
                        {{ form.nma_cost }}
                        {{ form.commercial_proposal }}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора источника НМА
    const nmaSourceRadios = document.querySelectorAll('input[name="nma_source"]');
    const existingNmaSection = document.getElementById('existing-nma-section');
    const newNmaSection = document.getElementById('new-nma-section');
    
    function toggleNmaSections() {
        const selectedValue = document.querySelector('input[name="nma_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingNmaSection.style.display = 'block';
            newNmaSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'block';
        } else {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'none';
        }
    }
    
    nmaSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleNmaSections);
    });
    toggleNmaSections(); // Инициализация
    
    // Обработка выбора источника коммерческого предложения
    const commercialSourceRadios = document.querySelectorAll('input[name="commercial_source"]');
    const existingCommercialSection = document.getElementById('existing-commercial-section');
    const newCommercialSection = document.getElementById('new-commercial-section');
    
    function toggleCommercialSections() {
        const selectedValue = document.querySelector('input[name="commercial_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingCommercialSection.style.display = 'block';
            newCommercialSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'block';
        } else {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'none';
        }
    }
    
    commercialSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleCommercialSections);
    });
    toggleCommercialSections(); // Инициализация
});
</script>
{% endblock %}

```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block main_content %}
<div class="container-fluid py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" id="calculation-form">
                        {% csrf_token %}
                        
                        <!-- Основные поля расчета -->
                        <h6 class="mb-3">Основная информация</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.project_name.label }}{% if form.project_name.field.required %} *{% endif %}</label>
                                {{ form.project_name }}
                                {% for error in form.project_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.client_name.label }}{% if form.client_name.field.required %} *{% endif %}</label>
                                {{ form.client_name }}
                                {% for error in form.client_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-12">
                                <label class="form-label">{{ form.project_brief.label }}{% if form.project_brief.field.required %} *{% endif %}</label>
                                {{ form.project_brief }}
                                {% for error in form.project_brief.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Выбор источника данных НМА -->
                        {% if form.nma_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных НМА</h6>
                        <div class="mb-4">
                            {% for choice in form.nma_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.nma_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующей формы НМА -->
                            {% if form.existing_nma.field.widget.input_type != 'hidden' %}
                            <div id="existing-nma-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_nma.label }}</label>
                                {{ form.existing_nma }}
                                {% for error in form.existing_nma.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания новой НМА -->
                            <div id="new-nma-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание новой формы НМА</h6>
                                        {% if nma_form %}
                                            {% for field in nma_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Выбор источника данных коммерческого предложения -->
                        {% if form.commercial_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных коммерческого предложения</h6>
                        <div class="mb-4">
                            {% for choice in form.commercial_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.commercial_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующего коммерческого предложения -->
                            {% if form.existing_commercial.field.widget.input_type != 'hidden' %}
                            <div id="existing-commercial-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_commercial.label }}</label>
                                {{ form.existing_commercial }}
                                {% for error in form.existing_commercial.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания нового коммерческого предложения -->
                            <div id="new-commercial-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание нового коммерческого предложения</h6>
                                        {% if commercial_form %}
                                            {% for field in commercial_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                            
                                            {% if service_formset %}
                                                <h6 class="mt-4">Услуги</h6>
                                                {{ service_formset.management_form }}
                                                <div id="service-items">
                                                    {% for form_item in service_formset %}
                                                        <div class="service-item mb-3 p-3 border rounded">
                                                            {% for field in form_item %}
                                                                {% if not field.is_hidden %}
                                                                    <div class="mb-2">
                                                                        <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                                        {{ field }}
                                                                        {% for error in field.errors %}
                                                                            <div class="text-danger small">{{ error }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% else %}
                                                                    {{ field }}
                                                                {% endif %}
                                                            {% endfor %}
                                                        </div>
                                                    {% endfor %}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Параметры расчета -->
                        <h6 class="mb-3">Параметры расчета</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.estimated_hours.label }}{% if form.estimated_hours.field.required %} *{% endif %}</label>
                                {{ form.estimated_hours }}
                                {% for error in form.estimated_hours.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.hourly_rate.label }}{% if form.hourly_rate.field.required %} *{% endif %}</label>
                                {{ form.hourly_rate }}
                                {% for error in form.hourly_rate.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.infrastructure_cost.label }}{% if form.infrastructure_cost.field.required %} *{% endif %}</label>
                                {{ form.infrastructure_cost }}
                                {% for error in form.infrastructure_cost.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.other_expenses.label }}{% if form.other_expenses.field.required %} *{% endif %}</label>
                                {{ form.other_expenses }}
                                {% for error in form.other_expenses.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.management_overhead_percent.label }}{% if form.management_overhead_percent.field.required %} *{% endif %}</label>
                                {{ form.management_overhead_percent }}
                                {% for error in form.management_overhead_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.risk_percent.label }}{% if form.risk_percent.field.required %} *{% endif %}</label>
                                {{ form.risk_percent }}
                                {% for error in form.risk_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.profit_margin_percent.label }}{% if form.profit_margin_percent.field.required %} *{% endif %}</label>
                                {{ form.profit_margin_percent }}
                                {% for error in form.profit_margin_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.asset_capitalization_percent.label }}{% if form.asset_capitalization_percent.field.required %} *{% endif %}</label>
                                {{ form.asset_capitalization_percent }}
                                {% for error in form.asset_capitalization_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.commercial_markup_percent.label }}{% if form.commercial_markup_percent.field.required %} *{% endif %}</label>
                                {{ form.commercial_markup_percent }}
                                {% for error in form.commercial_markup_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Скрытые поля -->
                        {{ form.nma_cost }}
                        {{ form.commercial_proposal }}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора источника НМА
    const nmaSourceRadios = document.querySelectorAll('input[name="nma_source"]');
    const existingNmaSection = document.getElementById('existing-nma-section');
    const newNmaSection = document.getElementById('new-nma-section');
    
    function toggleNmaSections() {
        const selectedValue = document.querySelector('input[name="nma_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingNmaSection.style.display = 'block';
            newNmaSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'block';
        } else {
            existingNmaSection.style.display = 'none';
            newNmaSection.style.display = 'none';
        }
    }
    
    nmaSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleNmaSections);
    });
    toggleNmaSections(); // Инициализация
    
    // Обработка выбора источника коммерческого предложения
    const commercialSourceRadios = document.querySelectorAll('input[name="commercial_source"]');
    const existingCommercialSection = document.getElementById('existing-commercial-section');
    const newCommercialSection = document.getElementById('new-commercial-section');
    
    function toggleCommercialSections() {
        const selectedValue = document.querySelector('input[name="commercial_source"]:checked')?.value;
        if (selectedValue === 'existing') {
            existingCommercialSection.style.display = 'block';
            newCommercialSection.style.display = 'none';
        } else if (selectedValue === 'new') {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'block';
        } else {
            existingCommercialSection.style.display = 'none';
            newCommercialSection.style.display = 'none';
        }
    }
    
    commercialSourceRadios.forEach(radio => {
        radio.addEventListener('change', toggleCommercialSections);
    });
    toggleCommercialSections(); // Инициализация
});
</script>
{% endblock %}

```

Обновляю JavaScript в шаблоне для корректной обработки скрытых полей:


```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block main_content %}
<div class="container-fluid py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" id="calculation-form">
                        {% csrf_token %}
                        
                        <!-- Основные поля расчета -->
                        <h6 class="mb-3">Основная информация</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.project_name.label }}{% if form.project_name.field.required %} *{% endif %}</label>
                                {{ form.project_name }}
                                {% for error in form.project_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.client_name.label }}{% if form.client_name.field.required %} *{% endif %}</label>
                                {{ form.client_name }}
                                {% for error in form.client_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-12">
                                <label class="form-label">{{ form.project_brief.label }}{% if form.project_brief.field.required %} *{% endif %}</label>
                                {{ form.project_brief }}
                                {% for error in form.project_brief.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Выбор источника данных НМА -->
                        {% if form.nma_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных НМА</h6>
                        <div class="mb-4">
                            {% for choice in form.nma_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.nma_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующей формы НМА -->
                            {% if form.existing_nma.field.widget.input_type != 'hidden' %}
                            <div id="existing-nma-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_nma.label }}</label>
                                {{ form.existing_nma }}
                                {% for error in form.existing_nma.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания новой НМА -->
                            <div id="new-nma-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание новой формы НМА</h6>
                                        {% if nma_form %}
                                            {% for field in nma_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Выбор источника данных коммерческого предложения -->
                        {% if form.commercial_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных коммерческого предложения</h6>
                        <div class="mb-4">
                            {% for choice in form.commercial_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.commercial_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующего коммерческого предложения -->
                            {% if form.existing_commercial.field.widget.input_type != 'hidden' %}
                            <div id="existing-commercial-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_commercial.label }}</label>
                                {{ form.existing_commercial }}
                                {% for error in form.existing_commercial.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания нового коммерческого предложения -->
                            <div id="new-commercial-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание нового коммерческого предложения</h6>
                                        {% if commercial_form %}
                                            {% for field in commercial_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                            
                                            {% if service_formset %}
                                                <h6 class="mt-4">Услуги</h6>
                                                {{ service_formset.management_form }}
                                                <div id="service-items">
                                                    {% for form_item in service_formset %}
                                                        <div class="service-item mb-3 p-3 border rounded">
                                                            {% for field in form_item %}
                                                                {% if not field.is_hidden %}
                                                                    <div class="mb-2">
                                                                        <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                                        {{ field }}
                                                                        {% for error in field.errors %}
                                                                            <div class="text-danger small">{{ error }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% else %}
                                                                    {{ field }}
                                                                {% endif %}
                                                            {% endfor %}
                                                        </div>
                                                    {% endfor %}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Параметры расчета -->
                        <h6 class="mb-3">Параметры расчета</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.estimated_hours.label }}{% if form.estimated_hours.field.required %} *{% endif %}</label>
                                {{ form.estimated_hours }}
                                {% for error in form.estimated_hours.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.hourly_rate.label }}{% if form.hourly_rate.field.required %} *{% endif %}</label>
                                {{ form.hourly_rate }}
                                {% for error in form.hourly_rate.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.infrastructure_cost.label }}{% if form.infrastructure_cost.field.required %} *{% endif %}</label>
                                {{ form.infrastructure_cost }}
                                {% for error in form.infrastructure_cost.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.other_expenses.label }}{% if form.other_expenses.field.required %} *{% endif %}</label>
                                {{ form.other_expenses }}
                                {% for error in form.other_expenses.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.management_overhead_percent.label }}{% if form.management_overhead_percent.field.required %} *{% endif %}</label>
                                {{ form.management_overhead_percent }}
                                {% for error in form.management_overhead_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.risk_percent.label }}{% if form.risk_percent.field.required %} *{% endif %}</label>
                                {{ form.risk_percent }}
                                {% for error in form.risk_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.profit_margin_percent.label }}{% if form.profit_margin_percent.field.required %} *{% endif %}</label>
                                {{ form.profit_margin_percent }}
                                {% for error in form.profit_margin_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.asset_capitalization_percent.label }}{% if form.asset_capitalization_percent.field.required %} *{% endif %}</label>
                                {{ form.asset_capitalization_percent }}
                                {% for error in form.asset_capitalization_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.commercial_markup_percent.label }}{% if form.commercial_markup_percent.field.required %} *{% endif %}</label>
                                {{ form.commercial_markup_percent }}
                                {% for error in form.commercial_markup_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Скрытые поля -->
                        {{ form.nma_cost }}
                        {{ form.commercial_proposal }}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора источника НМА
    const nmaSourceRadios = document.querySelectorAll('input[name="nma_source"]');
    const existingNmaSection = document.getElementById('existing-nma-section');
    const newNmaSection = document.getElementById('new-nma-section');
    
    if (nmaSourceRadios.length > 0 && existingNmaSection && newNmaSection) {
        function toggleNmaSections() {
            const selectedValue = document.querySelector('input[name="nma_source"]:checked')?.value;
            if (selectedValue === 'existing') {
                existingNmaSection.style.display = 'block';
                newNmaSection.style.display = 'none';
            } else if (selectedValue === 'new') {
                existingNmaSection.style.display = 'none';
                newNmaSection.style.display = 'block';
            } else {
                existingNmaSection.style.display = 'none';
                newNmaSection.style.display = 'none';
            }
        }
        
        nmaSourceRadios.forEach(radio => {
            radio.addEventListener('change', toggleNmaSections);
        });
        toggleNmaSections(); // Инициализация
    }
    
    // Обработка выбора источника коммерческого предложения
    const commercialSourceRadios = document.querySelectorAll('input[name="commercial_source"]');
    const existingCommercialSection = document.getElementById('existing-commercial-section');
    const newCommercialSection = document.getElementById('new-commercial-section');
    
    if (commercialSourceRadios.length > 0 && existingCommercialSection && newCommercialSection) {
        function toggleCommercialSections() {
            const selectedValue = document.querySelector('input[name="commercial_source"]:checked')?.value;
            if (selectedValue === 'existing') {
                existingCommercialSection.style.display = 'block';
                newCommercialSection.style.display = 'none';
            } else if (selectedValue === 'new') {
                existingCommercialSection.style.display = 'none';
                newCommercialSection.style.display = 'block';
            } else {
                existingCommercialSection.style.display = 'none';
                newCommercialSection.style.display = 'none';
            }
        }
        
        commercialSourceRadios.forEach(radio => {
            radio.addEventListener('change', toggleCommercialSections);
        });
        toggleCommercialSections(); // Инициализация
    }
});
</script>
{% endblock %}

```

Проверяю корректность обработки форм в views. Исправляю обработку данных формы:


Проверяю корректность обработки форм. Добавляю проверку на пустые значения в views:


```python
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except (NMACost.DoesNotExist, ValueError):
                    pass
```

```python
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id and commercial_id != '':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except (CommercialProposal.DoesNotExist, ValueError):
                    pass
```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        form = self.form_class(request.POST)
        context = {"form": form}
        
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
                # Если форма НМА невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id:
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except:
                    pass
        
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
                # Если форма коммерческого предложения невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id:
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except:
                    pass
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            if nma_cost:
                calculation.nma_cost = nma_cost
            if commercial_proposal:
                calculation.commercial_proposal = commercial_proposal
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
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
            if commercial_id:
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except:
                    pass
        elif form.data.get("commercial_source") == "none":
            commercial_proposal = None
        
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            # Привязываем созданные или выбранные формы
            if nma_cost is not None:
                updated.nma_cost = nma_cost
            if commercial_proposal is not None:
                updated.commercial_proposal = commercial_proposal
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

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        form = self.form_class(request.POST)
        context = {"form": form}
        
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
                # Если форма НМА невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id:
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except:
                    pass
        
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
                # Если форма коммерческого предложения невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id:
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except:
                    pass
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            if nma_cost:
                calculation.nma_cost = nma_cost
            if commercial_proposal:
                calculation.commercial_proposal = commercial_proposal
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
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
        
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            # Привязываем созданные или выбранные формы
            if nma_cost is not None:
                updated.nma_cost = nma_cost
            if commercial_proposal is not None:
                updated.commercial_proposal = commercial_proposal
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

```

Исправляю дублирующиеся части кода в views:


Исправляю оставшиеся вхождения в CostCalculationCreateView:


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        form = self.form_class(request.POST)
        context = {"form": form}
        
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
                # Если форма НМА невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except (NMACost.DoesNotExist, ValueError):
                    pass
        
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
                # Если форма коммерческого предложения невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id and commercial_id != '':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except (CommercialProposal.DoesNotExist, ValueError):
                    pass
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            if nma_cost:
                calculation.nma_cost = nma_cost
            if commercial_proposal:
                calculation.commercial_proposal = commercial_proposal
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
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
        
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            # Привязываем созданные или выбранные формы
            if nma_cost is not None:
                updated.nma_cost = nma_cost
            if commercial_proposal is not None:
                updated.commercial_proposal = commercial_proposal
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

```

## Выполненные модификации

### 1. **Сайдбар**
- Создан базовый шаблон `base_with_sidebar.html` с сайдбаром
- Все шаблоны itcost используют этот базовый шаблон
- Сайдбар включает ссылку на "Систему расчета стоимости"

### 2. **Интеграция с формами НМА и коммерческого предложения**
- Добавлены связи в модель `CostCalculation`:
  - `nma_cost` (ForeignKey к `NMACost`)
  - `commercial_proposal` (ForeignKey к `CommercialProposal`)
- Форма расчета позволяет:
  - Выбрать существующую форму НМА
  - Создать новую форму НМА прямо из формы расчета
  - Выбрать существующее коммерческое предложение
  - Создать новое коммерческое предложение прямо из формы расчета

### 3. **Обновленные шаблоны**
- Форма расчета (`cost_calculation_form.html`):
  - Радиокнопки для выбора источника данных
  - Динамическое отображение форм создания через JavaScript
  - Интеграция форм создания НМА и коммерческого предложения
- Детальный просмотр показывает информацию о связанных формах

### 4. **Обработка в views**
- Создание/редактирование расчетов обрабатывает:
  - Выбор существующих форм
  - Создание новых форм НМА и коммерческого предложения
  - Привязку созданных форм к расчету

### 5. **Миграции**
- Создана и применена миграция для добавления полей связей

Система расчета стоимости интегрирована с формами НМА и коммерческого предложения, использует единый сайдбар и позволяет выбирать существующие или создавать новые формы прямо из интерфейса расчета.

---

**User**

не работает кнопка создать расчет в системе расчета стоимости

---

**Cursor**

Проверяю проблему с кнопкой «Создать расчет». Изучаю код и проверяю возможные ошибки.


Проверяю обработку формы и возможные проблемы. Просматриваю форму и логику валидации:


Проверяю обработку скрытых полей `nma_cost` и `commercial_proposal` в форме. Исправляю логику валидации и сохранения:


Проблема: скрытые поля `nma_cost` и `commercial_proposal` не заполняются до валидации. Обновляю форму, чтобы устанавливать их значения перед валидацией:


```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if HAS_NMA else forms.ModelChoiceField.empty_queryset,
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if HAS_COMMERCIAL else forms.ModelChoiceField.empty_queryset,
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
            self.fields['nma_cost'].required = False
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
            self.fields['commercial_proposal'].required = False
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        form = self.form_class(request.POST)
        context = {"form": form}
        
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
                # Если форма НМА невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except (NMACost.DoesNotExist, ValueError):
                    pass
        
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
                # Если форма коммерческого предложения невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id and commercial_id != '':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except (CommercialProposal.DoesNotExist, ValueError):
                    pass
        
        # Устанавливаем значения скрытых полей перед валидацией
        if nma_cost:
            form.data = form.data.copy()
            form.data['nma_cost'] = str(nma_cost.pk)
        elif form.data.get("nma_source") in ("none", None, ""):
            form.data = form.data.copy()
            form.data['nma_cost'] = ""
        
        if commercial_proposal:
            form.data = form.data.copy()
            form.data['commercial_proposal'] = str(commercial_proposal.pk)
        elif form.data.get("commercial_source") in ("none", None, ""):
            form.data = form.data.copy()
            form.data['commercial_proposal'] = ""
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            if nma_cost:
                calculation.nma_cost = nma_cost
            else:
                calculation.nma_cost = None
            if commercial_proposal:
                calculation.commercial_proposal = commercial_proposal
            else:
                calculation.commercial_proposal = None
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
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
        
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            # Привязываем созданные или выбранные формы
            if nma_cost is not None:
                updated.nma_cost = nma_cost
            if commercial_proposal is not None:
                updated.commercial_proposal = commercial_proposal
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

```

Исправляю обработку данных формы: `form.data` — неизменяемый QueryDict. Используем правильный подход:


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        form = self.form_class(request.POST)
        context = {"form": form}
        
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
                # Если форма НМА невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except (NMACost.DoesNotExist, ValueError):
                    pass
        
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
                # Если форма коммерческого предложения невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id and commercial_id != '':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except (CommercialProposal.DoesNotExist, ValueError):
                    pass
        
        # Создаем копию данных формы для установки значений скрытых полей
        form_data = request.POST.copy()
        
        # Устанавливаем значения скрытых полей
        if nma_cost:
            form_data['nma_cost'] = str(nma_cost.pk)
        else:
            form_data['nma_cost'] = ""
        
        if commercial_proposal:
            form_data['commercial_proposal'] = str(commercial_proposal.pk)
        else:
            form_data['commercial_proposal'] = ""
        
        # Создаем новую форму с обновленными данными
        form = self.form_class(form_data)
        context["form"] = form
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            if nma_cost:
                calculation.nma_cost = nma_cost
            else:
                calculation.nma_cost = None
            if commercial_proposal:
                calculation.commercial_proposal = commercial_proposal
            else:
                calculation.commercial_proposal = None
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
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
        
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = calculation.created_by or request.user
            # Привязываем созданные или выбранные формы
            if nma_cost is not None:
                updated.nma_cost = nma_cost
            if commercial_proposal is not None:
                updated.commercial_proposal = commercial_proposal
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

```

Обновляю метод UpdateView аналогично:


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        form = self.form_class(request.POST)
        context = {"form": form}
        
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
                # Если форма НМА невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("nma_source") == "existing":
            nma_id = form.data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                except (NMACost.DoesNotExist, ValueError):
                    pass
        
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
                # Если форма коммерческого предложения невалидна, показываем ошибки
                return self.render_to_response(context)
        elif form.data.get("commercial_source") == "existing":
            commercial_id = form.data.get("existing_commercial")
            if commercial_id and commercial_id != '':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                except (CommercialProposal.DoesNotExist, ValueError):
                    pass
        
        # Создаем копию данных формы для установки значений скрытых полей
        form_data = request.POST.copy()
        
        # Устанавливаем значения скрытых полей
        if nma_cost:
            form_data['nma_cost'] = str(nma_cost.pk)
        else:
            form_data['nma_cost'] = ""
        
        if commercial_proposal:
            form_data['commercial_proposal'] = str(commercial_proposal.pk)
        else:
            form_data['commercial_proposal'] = ""
        
        # Создаем новую форму с обновленными данными
        form = self.form_class(form_data)
        context["form"] = form
        
        if form.is_valid():
            calculation = form.save(commit=False)
            calculation.created_by = request.user
            # Привязываем созданные или выбранные формы
            if nma_cost:
                calculation.nma_cost = nma_cost
            else:
                calculation.nma_cost = None
            if commercial_proposal:
                calculation.commercial_proposal = commercial_proposal
            else:
                calculation.commercial_proposal = None
            calculation.save()
            messages.success(request, "Расчет успешно создан.")
            return redirect("itcost:calculation_detail", pk=calculation.pk)
        
        # Если основная форма невалидна, добавляем пустые формы для отображения
        if HAS_NMA and "nma_form" not in context:
            context["nma_form"] = NMACostForm()
        if HAS_COMMERCIAL and "commercial_form" not in context:
            context["commercial_form"] = CommercialProposalForm()
            context["service_formset"] = ServiceItemFormSet()
        
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

```

Проверяю, что скрытые поля корректно отображаются в шаблоне:


Проверяю, что скрытые поля корректно отображаются в шаблоне. Добавляю отображение ошибок формы:


```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block main_content %}
<div class="container-fluid py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" id="calculation-form">
                        {% csrf_token %}
                        
                        <!-- Общие ошибки формы -->
                        {% if form.non_field_errors %}
                            <div class="alert alert-danger">
                                {% for error in form.non_field_errors %}
                                    <div>{{ error }}</div>
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        <!-- Основные поля расчета -->
                        <h6 class="mb-3">Основная информация</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.project_name.label }}{% if form.project_name.field.required %} *{% endif %}</label>
                                {{ form.project_name }}
                                {% for error in form.project_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.client_name.label }}{% if form.client_name.field.required %} *{% endif %}</label>
                                {{ form.client_name }}
                                {% for error in form.client_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-12">
                                <label class="form-label">{{ form.project_brief.label }}{% if form.project_brief.field.required %} *{% endif %}</label>
                                {{ form.project_brief }}
                                {% for error in form.project_brief.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Выбор источника данных НМА -->
                        {% if form.nma_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных НМА</h6>
                        <div class="mb-4">
                            {% for choice in form.nma_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.nma_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующей формы НМА -->
                            {% if form.existing_nma.field.widget.input_type != 'hidden' %}
                            <div id="existing-nma-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_nma.label }}</label>
                                {{ form.existing_nma }}
                                {% for error in form.existing_nma.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания новой НМА -->
                            <div id="new-nma-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание новой формы НМА</h6>
                                        {% if nma_form %}
                                            {% for field in nma_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Выбор источника данных коммерческого предложения -->
                        {% if form.commercial_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных коммерческого предложения</h6>
                        <div class="mb-4">
                            {% for choice in form.commercial_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.commercial_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующего коммерческого предложения -->
                            {% if form.existing_commercial.field.widget.input_type != 'hidden' %}
                            <div id="existing-commercial-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_commercial.label }}</label>
                                {{ form.existing_commercial }}
                                {% for error in form.existing_commercial.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания нового коммерческого предложения -->
                            <div id="new-commercial-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание нового коммерческого предложения</h6>
                                        {% if commercial_form %}
                                            {% for field in commercial_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                            
                                            {% if service_formset %}
                                                <h6 class="mt-4">Услуги</h6>
                                                {{ service_formset.management_form }}
                                                <div id="service-items">
                                                    {% for form_item in service_formset %}
                                                        <div class="service-item mb-3 p-3 border rounded">
                                                            {% for field in form_item %}
                                                                {% if not field.is_hidden %}
                                                                    <div class="mb-2">
                                                                        <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                                        {{ field }}
                                                                        {% for error in field.errors %}
                                                                            <div class="text-danger small">{{ error }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% else %}
                                                                    {{ field }}
                                                                {% endif %}
                                                            {% endfor %}
                                                        </div>
                                                    {% endfor %}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Параметры расчета -->
                        <h6 class="mb-3">Параметры расчета</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.estimated_hours.label }}{% if form.estimated_hours.field.required %} *{% endif %}</label>
                                {{ form.estimated_hours }}
                                {% for error in form.estimated_hours.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.hourly_rate.label }}{% if form.hourly_rate.field.required %} *{% endif %}</label>
                                {{ form.hourly_rate }}
                                {% for error in form.hourly_rate.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.infrastructure_cost.label }}{% if form.infrastructure_cost.field.required %} *{% endif %}</label>
                                {{ form.infrastructure_cost }}
                                {% for error in form.infrastructure_cost.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.other_expenses.label }}{% if form.other_expenses.field.required %} *{% endif %}</label>
                                {{ form.other_expenses }}
                                {% for error in form.other_expenses.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.management_overhead_percent.label }}{% if form.management_overhead_percent.field.required %} *{% endif %}</label>
                                {{ form.management_overhead_percent }}
                                {% for error in form.management_overhead_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.risk_percent.label }}{% if form.risk_percent.field.required %} *{% endif %}</label>
                                {{ form.risk_percent }}
                                {% for error in form.risk_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.profit_margin_percent.label }}{% if form.profit_margin_percent.field.required %} *{% endif %}</label>
                                {{ form.profit_margin_percent }}
                                {% for error in form.profit_margin_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.asset_capitalization_percent.label }}{% if form.asset_capitalization_percent.field.required %} *{% endif %}</label>
                                {{ form.asset_capitalization_percent }}
                                {% for error in form.asset_capitalization_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.commercial_markup_percent.label }}{% if form.commercial_markup_percent.field.required %} *{% endif %}</label>
                                {{ form.commercial_markup_percent }}
                                {% for error in form.commercial_markup_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Скрытые поля -->
                        {{ form.nma_cost }}
                        {{ form.commercial_proposal }}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора источника НМА
    const nmaSourceRadios = document.querySelectorAll('input[name="nma_source"]');
    const existingNmaSection = document.getElementById('existing-nma-section');
    const newNmaSection = document.getElementById('new-nma-section');
    
    if (nmaSourceRadios.length > 0 && existingNmaSection && newNmaSection) {
        function toggleNmaSections() {
            const selectedValue = document.querySelector('input[name="nma_source"]:checked')?.value;
            if (selectedValue === 'existing') {
                existingNmaSection.style.display = 'block';
                newNmaSection.style.display = 'none';
            } else if (selectedValue === 'new') {
                existingNmaSection.style.display = 'none';
                newNmaSection.style.display = 'block';
            } else {
                existingNmaSection.style.display = 'none';
                newNmaSection.style.display = 'none';
            }
        }
        
        nmaSourceRadios.forEach(radio => {
            radio.addEventListener('change', toggleNmaSections);
        });
        toggleNmaSections(); // Инициализация
    }
    
    // Обработка выбора источника коммерческого предложения
    const commercialSourceRadios = document.querySelectorAll('input[name="commercial_source"]');
    const existingCommercialSection = document.getElementById('existing-commercial-section');
    const newCommercialSection = document.getElementById('new-commercial-section');
    
    if (commercialSourceRadios.length > 0 && existingCommercialSection && newCommercialSection) {
        function toggleCommercialSections() {
            const selectedValue = document.querySelector('input[name="commercial_source"]:checked')?.value;
            if (selectedValue === 'existing') {
                existingCommercialSection.style.display = 'block';
                newCommercialSection.style.display = 'none';
            } else if (selectedValue === 'new') {
                existingCommercialSection.style.display = 'none';
                newCommercialSection.style.display = 'block';
            } else {
                existingCommercialSection.style.display = 'none';
                newCommercialSection.style.display = 'none';
            }
        }
        
        commercialSourceRadios.forEach(radio => {
            radio.addEventListener('change', toggleCommercialSections);
        });
        toggleCommercialSections(); // Инициализация
    }
});
</script>
{% endblock %}

```

Упрощаю логику обработки формы. Проблема может быть в двойном создании формы. Исправляю:


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
        # Обработка создания новой формы НМА
        nma_cost = None
        if HAS_NMA and form_data.get("nma_source") == "new":
            nma_form = NMACostForm(request.POST)
            context["nma_form"] = nma_form
            if nma_form.is_valid():
                nma_cost = nma_form.save(commit=False)
                nma_cost.total_cost = 0
                nma_cost.save()
                form_data['nma_cost'] = str(nma_cost.pk)
            else:
                # Если форма НМА невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_COMMERCIAL:
                    context["commercial_form"] = CommercialProposalForm()
                    context["service_formset"] = ServiceItemFormSet()
                return self.render_to_response(context)
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    form_data['nma_cost'] = str(nma_cost.pk)
                except (NMACost.DoesNotExist, ValueError):
                    form_data['nma_cost'] = ""
            else:
                form_data['nma_cost'] = ""
        else:
            form_data['nma_cost'] = ""
        
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
                form_data['commercial_proposal'] = str(commercial_proposal.pk)
            else:
                # Если форма коммерческого предложения невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_NMA and "nma_form" not in context:
                    context["nma_form"] = NMACostForm()
                return self.render_to_response(context)
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    form_data['commercial_proposal'] = str(commercial_proposal.pk)
                except (CommercialProposal.DoesNotExist, ValueError):
                    form_data['commercial_proposal'] = ""
            else:
                form_data['commercial_proposal'] = ""
        else:
            form_data['commercial_proposal'] = ""
        
        # Создаем форму с обновленными данными
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

```

Исправления внесены. Резюмирую изменения:

## Исправления для кнопки "Создать расчет"

### Проблемы, которые были исправлены:

1. **Скрытые поля не заполнялись до валидации**
   - Поля `nma_cost` и `commercial_proposal` были скрыты, но их значения не устанавливались перед валидацией формы
   - Исправление: значения устанавливаются в `form_data` перед созданием формы

2. **Обработка данных формы**
   - Форма создавалась дважды, что могло вызывать проблемы
   - Исправление: сначала обрабатываются вложенные формы (НМА и коммерческое предложение), затем создается основная форма с правильными значениями

3. **Обязательность полей**
   - Скрытые поля были обязательными
   - Исправление: добавлено `required=False` для полей `nma_cost` и `commercial_proposal`

4. **Отображение ошибок**
   - В шаблон добавлен блок для отображения общих ошибок формы

### Что теперь работает:

- Кнопка "Создать расчет" создает новый расчет
- Форма корректно обрабатывает случаи без выбора НМА или коммерческого предложения
- При создании новых форм НМА или коммерческого предложения они корректно привязываются к расчету
- Ошибки валидации отображаются пользователю

Проверьте создание расчета. Если проблема сохраняется, сообщите, какая именно ошибка появляется.

---

**User**

при введении следующих данных кнопка создать расчет все еще не работает

---

**Cursor**

Проверяю обработку формы и добавляю отладочную информацию, чтобы выяснить причину.


Улучшаю отображение ошибок валидации и проверяю обработку формы. Добавляю отладочную информацию:


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
        # Обработка создания новой формы НМА
        nma_cost = None
        if HAS_NMA and form_data.get("nma_source") == "new":
            nma_form = NMACostForm(request.POST)
            context["nma_form"] = nma_form
            if nma_form.is_valid():
                nma_cost = nma_form.save(commit=False)
                nma_cost.total_cost = 0
                nma_cost.save()
                form_data['nma_cost'] = str(nma_cost.pk)
            else:
                # Если форма НМА невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_COMMERCIAL:
                    context["commercial_form"] = CommercialProposalForm()
                    context["service_formset"] = ServiceItemFormSet()
                return self.render_to_response(context)
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    form_data['nma_cost'] = str(nma_cost.pk)
                except (NMACost.DoesNotExist, ValueError):
                    form_data['nma_cost'] = ""
            else:
                form_data['nma_cost'] = ""
        else:
            form_data['nma_cost'] = ""
        
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
                form_data['commercial_proposal'] = str(commercial_proposal.pk)
            else:
                # Если форма коммерческого предложения невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_NMA and "nma_form" not in context:
                    context["nma_form"] = NMACostForm()
                return self.render_to_response(context)
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    form_data['commercial_proposal'] = str(commercial_proposal.pk)
                except (CommercialProposal.DoesNotExist, ValueError):
                    form_data['commercial_proposal'] = ""
            else:
                form_data['commercial_proposal'] = ""
        else:
            form_data['commercial_proposal'] = ""
        
        # Создаем форму с обновленными данными
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation|default_if_none:"Новый расчет" }}{% endblock %}

{% block main_content %}
<div class="container-fluid py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10 col-xl-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">
                        {% if calculation %}
                            Редактирование расчета: {{ calculation.project_name }}
                        {% else %}
                            Новый расчет стоимости
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" id="calculation-form">
                        {% csrf_token %}
                        
                        <!-- Общие ошибки формы -->
                        {% if form.non_field_errors %}
                            <div class="alert alert-danger">
                                {% for error in form.non_field_errors %}
                                    <div>{{ error }}</div>
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        <!-- Сообщения Django -->
                        {% if messages %}
                            <div class="mb-3">
                                {% for message in messages %}
                                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                                        {{ message }}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                                    </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        <!-- Основные поля расчета -->
                        <h6 class="mb-3">Основная информация</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.project_name.label }}{% if form.project_name.field.required %} *{% endif %}</label>
                                {{ form.project_name }}
                                {% for error in form.project_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.client_name.label }}{% if form.client_name.field.required %} *{% endif %}</label>
                                {{ form.client_name }}
                                {% for error in form.client_name.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-12">
                                <label class="form-label">{{ form.project_brief.label }}{% if form.project_brief.field.required %} *{% endif %}</label>
                                {{ form.project_brief }}
                                {% for error in form.project_brief.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Выбор источника данных НМА -->
                        {% if form.nma_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных НМА</h6>
                        <div class="mb-4">
                            {% for choice in form.nma_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.nma_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующей формы НМА -->
                            {% if form.existing_nma.field.widget.input_type != 'hidden' %}
                            <div id="existing-nma-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_nma.label }}</label>
                                {{ form.existing_nma }}
                                {% for error in form.existing_nma.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания новой НМА -->
                            <div id="new-nma-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание новой формы НМА</h6>
                                        {% if nma_form %}
                                            {% for field in nma_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Выбор источника данных коммерческого предложения -->
                        {% if form.commercial_source.field.widget.input_type != 'hidden' %}
                        <h6 class="mb-3">Источник данных коммерческого предложения</h6>
                        <div class="mb-4">
                            {% for choice in form.commercial_source %}
                                <div class="form-check mb-2">
                                    {{ choice.tag }}
                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                        {{ choice.choice_label }}
                                    </label>
                                </div>
                            {% endfor %}
                            {% for error in form.commercial_source.errors %}
                                <div class="text-danger small">{{ error }}</div>
                            {% endfor %}
                            
                            <!-- Выбор существующего коммерческого предложения -->
                            {% if form.existing_commercial.field.widget.input_type != 'hidden' %}
                            <div id="existing-commercial-section" class="mt-3" style="display: none;">
                                <label class="form-label">{{ form.existing_commercial.label }}</label>
                                {{ form.existing_commercial }}
                                {% for error in form.existing_commercial.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            <!-- Форма создания нового коммерческого предложения -->
                            <div id="new-commercial-section" class="mt-3" style="display: none;">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">Создание нового коммерческого предложения</h6>
                                        {% if commercial_form %}
                                            {% for field in commercial_form %}
                                                <div class="mb-3">
                                                    <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                    {{ field }}
                                                    {% for error in field.errors %}
                                                        <div class="text-danger small">{{ error }}</div>
                                                    {% endfor %}
                                                </div>
                                            {% endfor %}
                                            
                                            {% if service_formset %}
                                                <h6 class="mt-4">Услуги</h6>
                                                {{ service_formset.management_form }}
                                                <div id="service-items">
                                                    {% for form_item in service_formset %}
                                                        <div class="service-item mb-3 p-3 border rounded">
                                                            {% for field in form_item %}
                                                                {% if not field.is_hidden %}
                                                                    <div class="mb-2">
                                                                        <label class="form-label">{{ field.label }}{% if field.field.required %} *{% endif %}</label>
                                                                        {{ field }}
                                                                        {% for error in field.errors %}
                                                                            <div class="text-danger small">{{ error }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% else %}
                                                                    {{ field }}
                                                                {% endif %}
                                                            {% endfor %}
                                                        </div>
                                                    {% endfor %}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endif %}

                        <!-- Параметры расчета -->
                        <h6 class="mb-3">Параметры расчета</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.estimated_hours.label }}{% if form.estimated_hours.field.required %} *{% endif %}</label>
                                {{ form.estimated_hours }}
                                {% for error in form.estimated_hours.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.hourly_rate.label }}{% if form.hourly_rate.field.required %} *{% endif %}</label>
                                {{ form.hourly_rate }}
                                {% for error in form.hourly_rate.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.infrastructure_cost.label }}{% if form.infrastructure_cost.field.required %} *{% endif %}</label>
                                {{ form.infrastructure_cost }}
                                {% for error in form.infrastructure_cost.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.other_expenses.label }}{% if form.other_expenses.field.required %} *{% endif %}</label>
                                {{ form.other_expenses }}
                                {% for error in form.other_expenses.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.management_overhead_percent.label }}{% if form.management_overhead_percent.field.required %} *{% endif %}</label>
                                {{ form.management_overhead_percent }}
                                {% for error in form.management_overhead_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.risk_percent.label }}{% if form.risk_percent.field.required %} *{% endif %}</label>
                                {{ form.risk_percent }}
                                {% for error in form.risk_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.profit_margin_percent.label }}{% if form.profit_margin_percent.field.required %} *{% endif %}</label>
                                {{ form.profit_margin_percent }}
                                {% for error in form.profit_margin_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.asset_capitalization_percent.label }}{% if form.asset_capitalization_percent.field.required %} *{% endif %}</label>
                                {{ form.asset_capitalization_percent }}
                                {% for error in form.asset_capitalization_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.commercial_markup_percent.label }}{% if form.commercial_markup_percent.field.required %} *{% endif %}</label>
                                {{ form.commercial_markup_percent }}
                                {% for error in form.commercial_markup_percent.errors %}
                                    <div class="text-danger small">{{ error }}</div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Скрытые поля -->
                        {{ form.nma_cost }}
                        {{ form.commercial_proposal }}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="{% url 'itcost:dashboard' %}" class="btn btn-link">Вернуться к дашборду</a>
                            <button type="submit" class="btn btn-primary">
                                {% if calculation %}Сохранить изменения{% else %}Создать расчет{% endif %}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора источника НМА
    const nmaSourceRadios = document.querySelectorAll('input[name="nma_source"]');
    const existingNmaSection = document.getElementById('existing-nma-section');
    const newNmaSection = document.getElementById('new-nma-section');
    
    if (nmaSourceRadios.length > 0 && existingNmaSection && newNmaSection) {
        function toggleNmaSections() {
            const selectedValue = document.querySelector('input[name="nma_source"]:checked')?.value;
            if (selectedValue === 'existing') {
                existingNmaSection.style.display = 'block';
                newNmaSection.style.display = 'none';
            } else if (selectedValue === 'new') {
                existingNmaSection.style.display = 'none';
                newNmaSection.style.display = 'block';
            } else {
                existingNmaSection.style.display = 'none';
                newNmaSection.style.display = 'none';
            }
        }
        
        nmaSourceRadios.forEach(radio => {
            radio.addEventListener('change', toggleNmaSections);
        });
        toggleNmaSections(); // Инициализация
    }
    
    // Обработка выбора источника коммерческого предложения
    const commercialSourceRadios = document.querySelectorAll('input[name="commercial_source"]');
    const existingCommercialSection = document.getElementById('existing-commercial-section');
    const newCommercialSection = document.getElementById('new-commercial-section');
    
    if (commercialSourceRadios.length > 0 && existingCommercialSection && newCommercialSection) {
        function toggleCommercialSections() {
            const selectedValue = document.querySelector('input[name="commercial_source"]:checked')?.value;
            if (selectedValue === 'existing') {
                existingCommercialSection.style.display = 'block';
                newCommercialSection.style.display = 'none';
            } else if (selectedValue === 'new') {
                existingCommercialSection.style.display = 'none';
                newCommercialSection.style.display = 'block';
            } else {
                existingCommercialSection.style.display = 'none';
                newCommercialSection.style.display = 'none';
            }
        }
        
        commercialSourceRadios.forEach(radio => {
            radio.addEventListener('change', toggleCommercialSections);
        });
        toggleCommercialSections(); // Инициализация
    }
});
</script>
{% endblock %}

```

Исправляю создание пустого queryset и проверяю обработку пустых значений для ForeignKey:


```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if HAS_NMA else NMACost.objects.none() if HAS_NMA else [],
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if HAS_COMMERCIAL else forms.ModelChoiceField.empty_queryset,
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
            self.fields['nma_cost'].required = False
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
            self.fields['commercial_proposal'].required = False
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if HAS_NMA else NMACost.objects.none() if HAS_NMA else [],
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if HAS_COMMERCIAL else CommercialProposal.objects.none() if HAS_COMMERCIAL else [],
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
            self.fields['nma_cost'].required = False
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
            self.fields['commercial_proposal'].required = False
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    HAS_NMA = True
except ImportError:
    HAS_NMA = False
    NMACost = None

try:
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_COMMERCIAL = True
except ImportError:
    HAS_COMMERCIAL = False
    CommercialProposal = None
```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if HAS_NMA and NMACost else [],
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if HAS_COMMERCIAL else CommercialProposal.objects.none() if HAS_COMMERCIAL else [],
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
            self.fields['nma_cost'].required = False
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
            self.fields['commercial_proposal'].required = False
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if HAS_NMA and NMACost else [],
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if HAS_COMMERCIAL and CommercialProposal else [],
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
            self.fields['nma_cost'].required = False
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
            self.fields['commercial_proposal'].required = False
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    form_data['nma_cost'] = str(nma_cost.pk)
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    form_data['nma_cost'] = ""
            else:
                form_data['nma_cost'] = ""
        else:
            form_data['nma_cost'] = ""
```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
        # Обработка создания новой формы НМА
        nma_cost = None
        if HAS_NMA and form_data.get("nma_source") == "new":
            nma_form = NMACostForm(request.POST)
            context["nma_form"] = nma_form
            if nma_form.is_valid():
                nma_cost = nma_form.save(commit=False)
                nma_cost.total_cost = 0
                nma_cost.save()
                form_data['nma_cost'] = str(nma_cost.pk)
            else:
                # Если форма НМА невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_COMMERCIAL:
                    context["commercial_form"] = CommercialProposalForm()
                    context["service_formset"] = ServiceItemFormSet()
                return self.render_to_response(context)
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    form_data['nma_cost'] = str(nma_cost.pk)
                except (NMACost.DoesNotExist, ValueError):
                    form_data['nma_cost'] = ""
            else:
                form_data['nma_cost'] = ""
        else:
            form_data['nma_cost'] = ""
        
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
                form_data['commercial_proposal'] = str(commercial_proposal.pk)
            else:
                # Если форма коммерческого предложения невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_NMA and "nma_form" not in context:
                    context["nma_form"] = NMACostForm()
                return self.render_to_response(context)
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    form_data['commercial_proposal'] = str(commercial_proposal.pk)
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    form_data['commercial_proposal'] = ""
            else:
                form_data['commercial_proposal'] = ""
        else:
            form_data['commercial_proposal'] = ""
        
        # Создаем форму с обновленными данными
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

Проверяю текущее состояние файла и исправляю проблему:


Исправляю queryset и добавляю проверку на пустые значения:


```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if (HAS_NMA and NMACost) else (NMACost.objects.none() if NMACost else []),
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if HAS_COMMERCIAL and CommercialProposal else [],
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
            self.fields['nma_cost'].required = False
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
            self.fields['commercial_proposal'].required = False
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if (HAS_NMA and NMACost) else (NMACost.objects.none() if NMACost else []),
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if (HAS_COMMERCIAL and CommercialProposal) else (CommercialProposal.objects.none() if CommercialProposal else []),
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
            self.fields['nma_cost'].required = False
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
            self.fields['commercial_proposal'].required = False
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }


```

```python
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        if 'nma_cost' in self.fields:
            self.fields['nma_cost'].widget = forms.HiddenInput()
            self.fields['nma_cost'].required = False
            # Разрешаем пустые значения для ForeignKey
            self.fields['nma_cost'].empty_label = None
        if 'commercial_proposal' in self.fields:
            self.fields['commercial_proposal'].widget = forms.HiddenInput()
            self.fields['commercial_proposal'].required = False
            # Разрешаем пустые значения для ForeignKey
            self.fields['commercial_proposal'].empty_label = None
```

Проверяю обработку пустых значений для ForeignKey. Добавляю более детальную обработку:


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
        # Обработка создания новой формы НМА
        nma_cost = None
        if HAS_NMA and form_data.get("nma_source") == "new":
            nma_form = NMACostForm(request.POST)
            context["nma_form"] = nma_form
            if nma_form.is_valid():
                nma_cost = nma_form.save(commit=False)
                nma_cost.total_cost = 0
                nma_cost.save()
                form_data['nma_cost'] = str(nma_cost.pk)
            else:
                # Если форма НМА невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_COMMERCIAL:
                    context["commercial_form"] = CommercialProposalForm()
                    context["service_formset"] = ServiceItemFormSet()
                return self.render_to_response(context)
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    form_data['nma_cost'] = str(nma_cost.pk)
                except (NMACost.DoesNotExist, ValueError):
                    form_data['nma_cost'] = ""
            else:
                form_data['nma_cost'] = ""
        else:
            form_data['nma_cost'] = ""
        
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
                form_data['commercial_proposal'] = str(commercial_proposal.pk)
            else:
                # Если форма коммерческого предложения невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_NMA and "nma_form" not in context:
                    context["nma_form"] = NMACostForm()
                return self.render_to_response(context)
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    form_data['commercial_proposal'] = str(commercial_proposal.pk)
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    form_data['commercial_proposal'] = ""
            else:
                form_data['commercial_proposal'] = ""
        else:
            form_data['commercial_proposal'] = ""
        
        # Убеждаемся, что пустые значения правильно обрабатываются
        # Для ForeignKey полей пустая строка должна быть удалена из данных, чтобы Django использовал None
        if form_data.get('nma_cost') == '':
            if 'nma_cost' in form_data:
                del form_data['nma_cost']
        if form_data.get('commercial_proposal') == '':
            if 'commercial_proposal' in form_data:
                del form_data['commercial_proposal']
        
        # Создаем форму с обновленными данными
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

## Исправления для кнопки "Создать расчет"

### Основные изменения:

1. **Обработка пустых значений для ForeignKey**
   - Для пустых значений удаляем поле из `form_data`, чтобы Django корректно обработал `None`
   - Добавлена проверка на `'None'` как строку

2. **Отображение ошибок валидации**
   - В шаблон добавлен блок для сообщений Django
   - В views добавлено логирование ошибок валидации с понятными сообщениями

3. **Улучшена обработка выбранных форм**
   - Более надежная обработка выбранных НМА и коммерческих предложений
   - Добавлена обработка исключений `TypeError`

4. **Исправлен queryset для полей выбора**
   - Исправлена логика создания queryset для `existing_nma` и `existing_commercial`

### Что теперь должно работать:

- Кнопка "Создать расчет" создает новый расчет
- При ошибках валидации отображаются понятные сообщения
- Корректно обрабатываются выбранные НМА и коммерческие предложения
- Пустые значения для ForeignKey обрабатываются правильно

Попробуйте снова создать расчет. Если проблема останется, проверьте сообщения об ошибках на странице — они покажут, какое поле вызывает проблему.

---

**User**

Кнока создать все еще не работает если выбирать уже существующие данные но работает если создавать  с нуля через функцию создать новую форму

---

**Cursor**

Проверяю обработку выбора существующих НМА и коммерческих предложений. Вероятно, проблема в установке значений для скрытых полей.


Исправляю обработку выбора существующих данных: корректно устанавливаю значения в `form_data` и проверяю их перед валидацией.


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
        # Обработка создания новой формы НМА
        nma_cost = None
        if HAS_NMA and form_data.get("nma_source") == "new":
            nma_form = NMACostForm(request.POST)
            context["nma_form"] = nma_form
            if nma_form.is_valid():
                nma_cost = nma_form.save(commit=False)
                nma_cost.total_cost = 0
                nma_cost.save()
                form_data['nma_cost'] = str(nma_cost.pk)
            else:
                # Если форма НМА невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_COMMERCIAL:
                    context["commercial_form"] = CommercialProposalForm()
                    context["service_formset"] = ServiceItemFormSet()
                return self.render_to_response(context)
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'nma_cost' in form_data:
                        form_data.pop('nma_cost', None)
            else:
                # Удаляем поле, если не выбрано
                if 'nma_cost' in form_data:
                    form_data.pop('nma_cost', None)
        else:
            # Удаляем поле, если не используется
            if 'nma_cost' in form_data:
                form_data.pop('nma_cost', None)
        
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
                form_data['commercial_proposal'] = str(commercial_proposal.pk)
            else:
                # Если форма коммерческого предложения невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_NMA and "nma_form" not in context:
                    context["nma_form"] = NMACostForm()
                return self.render_to_response(context)
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    form_data['commercial_proposal'] = str(commercial_proposal.pk)
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    form_data['commercial_proposal'] = ""
            else:
                form_data['commercial_proposal'] = ""
        else:
            form_data['commercial_proposal'] = ""
        
        # Убеждаемся, что пустые значения правильно обрабатываются
        # Для ForeignKey полей пустая строка должна быть удалена из данных, чтобы Django использовал None
        if form_data.get('nma_cost') == '':
            if 'nma_cost' in form_data:
                del form_data['nma_cost']
        if form_data.get('commercial_proposal') == '':
            if 'commercial_proposal' in form_data:
                del form_data['commercial_proposal']
        
        # Создаем форму с обновленными данными
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
        # Обработка создания новой формы НМА
        nma_cost = None
        if HAS_NMA and form_data.get("nma_source") == "new":
            nma_form = NMACostForm(request.POST)
            context["nma_form"] = nma_form
            if nma_form.is_valid():
                nma_cost = nma_form.save(commit=False)
                nma_cost.total_cost = 0
                nma_cost.save()
                form_data['nma_cost'] = str(nma_cost.pk)
            else:
                # Если форма НМА невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_COMMERCIAL:
                    context["commercial_form"] = CommercialProposalForm()
                    context["service_formset"] = ServiceItemFormSet()
                return self.render_to_response(context)
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'nma_cost' in form_data:
                        form_data.pop('nma_cost', None)
            else:
                # Удаляем поле, если не выбрано
                if 'nma_cost' in form_data:
                    form_data.pop('nma_cost', None)
        else:
            # Удаляем поле, если не используется
            if 'nma_cost' in form_data:
                form_data.pop('nma_cost', None)
        
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
                form_data['commercial_proposal'] = str(commercial_proposal.pk)
            else:
                # Если форма коммерческого предложения невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_NMA and "nma_form" not in context:
                    context["nma_form"] = NMACostForm()
                return self.render_to_response(context)
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'commercial_proposal' in form_data:
                        form_data.pop('commercial_proposal', None)
            else:
                # Удаляем поле, если не выбрано
                if 'commercial_proposal' in form_data:
                    form_data.pop('commercial_proposal', None)
        else:
            # Удаляем поле, если не используется
            if 'commercial_proposal' in form_data:
                form_data.pop('commercial_proposal', None)
        
        # Убеждаемся, что пустые значения правильно обрабатываются
        # Для ForeignKey полей пустая строка должна быть удалена из данных, чтобы Django использовал None
        if form_data.get('nma_cost') == '':
            if 'nma_cost' in form_data:
                del form_data['nma_cost']
        if form_data.get('commercial_proposal') == '':
            if 'commercial_proposal' in form_data:
                del form_data['commercial_proposal']
        
        # Создаем форму с обновленными данными
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
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
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'nma_cost' in form_data:
                        form_data.pop('nma_cost', None)
            else:
                # Удаляем поле, если не выбрано
                if 'nma_cost' in form_data:
                    form_data.pop('nma_cost', None)
        else:
            # Удаляем поле, если не используется
            if 'nma_cost' in form_data:
                form_data.pop('nma_cost', None)
        
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
                form_data['commercial_proposal'] = str(commercial_proposal.pk)
            else:
                # Если форма коммерческого предложения невалидна, показываем ошибки
                form = self.form_class(form_data)
                context["form"] = form
                if HAS_NMA and "nma_form" not in context:
                    context["nma_form"] = NMACostForm()
                return self.render_to_response(context)
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'commercial_proposal' in form_data:
                        form_data.pop('commercial_proposal', None)
            else:
                # Удаляем поле, если не выбрано
                if 'commercial_proposal' in form_data:
                    form_data.pop('commercial_proposal', None)
        else:
            # Удаляем поле, если не используется
            if 'commercial_proposal' in form_data:
                form_data.pop('commercial_proposal', None)
        
        # Убеждаемся, что пустые значения правильно обрабатываются
        # Для ForeignKey полей пустая строка должна быть удалена из данных, чтобы Django использовал None
        if form_data.get('nma_cost') == '':
            if 'nma_cost' in form_data:
                del form_data['nma_cost']
        if form_data.get('commercial_proposal') == '':
            if 'commercial_proposal' in form_data:
                del form_data['commercial_proposal']
        
        # Создаем форму с обновленными данными
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
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
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'nma_cost' in form_data:
                        form_data.pop('nma_cost', None)
            else:
                # Удаляем поле, если не выбрано
                if 'nma_cost' in form_data:
                    form_data.pop('nma_cost', None)
        else:
            # Удаляем поле, если не используется
            if 'nma_cost' in form_data:
                form_data.pop('nma_cost', None)
        
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
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'commercial_proposal' in form_data:
                        form_data.pop('commercial_proposal', None)
            else:
                # Удаляем поле, если не выбрано
                if 'commercial_proposal' in form_data:
                    form_data.pop('commercial_proposal', None)
        else:
            # Удаляем поле, если не используется
            if 'commercial_proposal' in form_data:
                form_data.pop('commercial_proposal', None)
        
        # Убеждаемся, что пустые значения правильно обрабатываются
        # Для ForeignKey полей пустая строка должна быть удалена из данных, чтобы Django использовал None
        if form_data.get('nma_cost') == '':
            if 'nma_cost' in form_data:
                del form_data['nma_cost']
        if form_data.get('commercial_proposal') == '':
            if 'commercial_proposal' in form_data:
                del form_data['commercial_proposal']
        
        # Создаем форму с обновленными данными
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        # Создаем копию данных для модификации
        form_data = request.POST.copy()
        context = {}
        
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
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'nma_cost' in form_data:
                        form_data.pop('nma_cost', None)
            else:
                # Удаляем поле, если не выбрано
                if 'nma_cost' in form_data:
                    form_data.pop('nma_cost', None)
        else:
            # Удаляем поле, если не используется
            if 'nma_cost' in form_data:
                form_data.pop('nma_cost', None)
        
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
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'commercial_proposal' in form_data:
                        form_data.pop('commercial_proposal', None)
            else:
                # Удаляем поле, если не выбрано
                if 'commercial_proposal' in form_data:
                    form_data.pop('commercial_proposal', None)
        else:
            # Удаляем поле, если не используется
            if 'commercial_proposal' in form_data:
                form_data.pop('commercial_proposal', None)
        
        # Создаем форму с обновленными данными
        # QueryDict уже обработан выше, пустые значения удалены
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

Проверяю, что значения корректно устанавливаются. Добавляю отладочную информацию для диагностики:


Проверяю корректность работы с QueryDict. Улучшаю обработку:


```python
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.shortcuts import redirect
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
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'nma_cost' in form_data:
                        form_data.pop('nma_cost', None)
            else:
                # Удаляем поле, если не выбрано
                if 'nma_cost' in form_data:
                    form_data.pop('nma_cost', None)
        else:
            # Удаляем поле, если не используется
            if 'nma_cost' in form_data:
                form_data.pop('nma_cost', None)
        
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
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'commercial_proposal' in form_data:
                        form_data.pop('commercial_proposal', None)
            else:
                # Удаляем поле, если не выбрано
                if 'commercial_proposal' in form_data:
                    form_data.pop('commercial_proposal', None)
        else:
            # Удаляем поле, если не используется
            if 'commercial_proposal' in form_data:
                form_data.pop('commercial_proposal', None)
        
        # Создаем форму с обновленными данными
        # QueryDict уже обработан выше, пустые значения удалены
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

Исправления внесены. Резюме изменений:

## Исправления для работы с существующими данными

### Основные изменения:

1. **Правильная работа с QueryDict**
   - Используется `setlist()` вместо прямого присваивания для установки значений в QueryDict
   - В начале удаляются скрытые поля из исходных данных, чтобы потом установить их корректно

2. **Улучшенная обработка выбора существующих данных**
   - Добавлена проверка на `'None'` как строку для `nma_id` (как было для `commercial_id`)
   - Используется `pop()` для удаления полей из QueryDict, когда они не нужны

3. **Единообразная обработка**
   - Логика обработки НМА и коммерческого предложения унифицирована
   - Обработка ошибок улучшена (добавлен `TypeError`)

### Что теперь должно работать:

- Выбор существующей формы НМА — значение корректно устанавливается в форму
- Выбор существующего коммерческого предложения — значение корректно устанавливается в форму
- Создание новых форм — продолжает работать как раньше
- Неиспользование НМА/коммерческого предложения — поля корректно удаляются

Попробуйте снова создать расчет, выбрав существующие данные. Если проблема останется, проверьте сообщения об ошибках на странице — они покажут, что именно не работает.

---

**User**

Добавь систему расчета стоимости в админку

---

**Cursor**

Проверяю текущую настройку админки и регистрирую модели системы расчета стоимости.


Модели уже зарегистрированы. Улучшаю админ-классы и добавляю их в навигацию Unfold:


```python
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import CostCalculation, OrganizationSettings, RoleAssignment


@admin.register(CostCalculation)
class CostCalculationAdmin(admin.ModelAdmin):
    list_display = (
        "project_name",
        "client_name",
        "development_cost_display",
        "intangible_asset_cost_display",
        "commercial_offer_cost_display",
        "nma_link",
        "commercial_link",
        "created_by",
        "created_at",
    )
    list_display_links = ("project_name",)
    search_fields = ("project_name", "client_name", "project_brief")
    list_filter = ("created_at", "created_by", "nma_cost", "commercial_proposal")
    readonly_fields = (
        "development_cost",
        "intangible_asset_cost",
        "commercial_offer_cost",
        "created_at",
        "updated_at",
        "created_by",
    )
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "project_name",
                    "client_name",
                    "project_brief",
                )
            },
        ),
        (
            "Параметры расчета",
            {
                "fields": (
                    "estimated_hours",
                    "hourly_rate",
                    "infrastructure_cost",
                    "other_expenses",
                    "management_overhead_percent",
                    "risk_percent",
                    "profit_margin_percent",
                )
            },
        ),
        (
            "Результаты расчета",
            {
                "fields": (
                    "development_cost",
                    "asset_capitalization_percent",
                    "intangible_asset_cost",
                    "commercial_markup_percent",
                    "commercial_offer_cost",
                )
            },
        ),
        (
            "Связанные данные",
            {
                "fields": (
                    "nma_cost",
                    "commercial_proposal",
                )
            },
        ),
        (
            "Метаданные",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    raw_id_fields = ("nma_cost", "commercial_proposal", "created_by")
    
    def development_cost_display(self, obj):
        """Отображение стоимости разработки с форматированием"""
        return format_html('<strong>{:,.2f} ₽</strong>', obj.development_cost)
    development_cost_display.short_description = "Стоимость разработки"
    
    def intangible_asset_cost_display(self, obj):
        """Отображение стоимости НМА с форматированием"""
        return format_html('<strong>{:,.2f} ₽</strong>', obj.intangible_asset_cost)
    intangible_asset_cost_display.short_description = "Стоимость НМА"
    
    def commercial_offer_cost_display(self, obj):
        """Отображение стоимости коммерческого предложения с форматированием"""
        return format_html('<strong>{:,.2f} ₽</strong>', obj.commercial_offer_cost)
    commercial_offer_cost_display.short_description = "Коммерческое предложение"
    
    def nma_link(self, obj):
        """Ссылка на связанную форму НМА"""
        if obj.nma_cost:
            url = reverse("admin:nmacost_nmacost_change", args=[obj.nma_cost.pk])
            return format_html('<a href="{}">{}</a>', url, obj.nma_cost)
        return "—"
    nma_link.short_description = "Форма НМА"
    
    def commercial_link(self, obj):
        """Ссылка на связанное коммерческое предложение"""
        if obj.commercial_proposal:
            url = reverse("admin:commercial_proposal_commercialproposal_change", args=[obj.commercial_proposal.pk])
            return format_html('<a href="{}">{}</a>', url, obj.commercial_proposal)
        return "—"
    commercial_link.short_description = "Коммерческое предложение"
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем создателя при создании"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "director_full_name",
        "director_position",
        "contact_phone",
        "contact_email",
        "updated_at",
    )
    fieldsets = (
        (
            "Информация о компании",
            {
                "fields": (
                    "company_name",
                    "logo",
                )
            },
        ),
        (
            "Руководитель",
            {
                "fields": (
                    "director_full_name",
                    "director_position",
                )
            },
        ),
        (
            "Контакты",
            {
                "fields": (
                    "contact_phone",
                    "contact_email",
                )
            },
        ),
        (
            "Метаданные",
            {
                "fields": ("updated_at",)
            },
        ),
    )
    readonly_fields = ("updated_at",)
    
    def has_add_permission(self, request):
        """Разрешаем создание только одной записи"""
        return not OrganizationSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление настроек организации"""
        return False


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role_display", "assigned_by", "assigned_at")
    list_filter = ("role", "assigned_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
    raw_id_fields = ("user", "assigned_by")
    readonly_fields = ("assigned_at",)
    
    fieldsets = (
        (
            "Назначение роли",
            {
                "fields": (
                    "user",
                    "role",
                    "assigned_by",
                    "assigned_at",
                )
            },
        ),
    )
    
    def role_display(self, obj):
        """Отображение роли с форматированием"""
        role_labels = {
            "global_admin": "Глобальный администратор",
            "commercial_director": "Коммерческий директор",
            "accountant": "Бухгалтер",
            "hr_specialist": "Кадровик",
        }
        return role_labels.get(obj.role, obj.role)
    role_display.short_description = "Роль"
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем назначившего при создании"""
        if not change:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)

```

```python
"""
Django settings for ez project.

Generated by 'django-admin startproject' using Django 5.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w+!(#_tbe8^=jq8s@i#l7++rv&zb_$u(z$5i@4+#vc__-88&p*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition



INSTALLED_APPS = [
    'unfold',  # Django Unfold должен быть перед django.contrib.admin
    'unfold.contrib.filters',  # Дополнительные фильтры
    'login',
    'workspace',
    'customers',
    'contractors',
    'equipment',
    'employees',
    'subcontractors',
    'staff.apps.StaffConfig',
    'workspace_control',
    'projects',
    'commercial_proposal',
    'nmacost',
    'itcost',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Для поддержки локализации
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ez.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ← эта строка теперь будет работать
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ez.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/auth/'

# settings.py
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False

# Django Unfold settings
UNFOLD = {
    "SITE_TITLE": "EZ Project Admin",
    "SITE_HEADER": "Административная панель",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_LOGO": None,
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "ez.settings.environment_callback",
    "DASHBOARD_CALLBACK": None,
    "LOGIN": {
        "image": None,
        "redirect_after": None,
    },
    "STYLES": [],
    "SCRIPTS": [],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇳🇱",
                "ru": "🇷🇺",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Главное",
                "separator": True,
                "items": [
                    {
                        "title": "Проекты",
                        "link": "/admin/projects/project/",
                    },
                    {
                        "title": "Коммерческие предложения",
                        "link": "/admin/commercial_proposal/commercialproposal/",
                    },
                    {
                        "title": "Расчеты стоимости",
                        "link": "/admin/itcost/costcalculation/",
                    },
                ],
            },
            {
                "title": "Контакты",
                "separator": True,
                "items": [
                    {
                        "title": "Заказчики",
                        "link": "/admin/customers/customer/",
                    },
                    {
                        "title": "Подрядчики",
                        "link": "/admin/contractors/contractor/",
                    },
                    {
                        "title": "Субподрядчики",
                        "link": "/admin/subcontractors/subcontractor/",
                    },
                    {
                        "title": "Сотрудники",
                        "link": "/admin/employees/employee/",
                    },
                ],
            },
            {
                "title": "Ресурсы",
                "separator": True,
                "items": [
                    {
                        "title": "Оборудование",
                        "link": "/admin/equipment/equipment/",
                    },
                    {
                        "title": "НМА",
                        "link": "/admin/nmacost/nmacost/",
                    },
                ],
            },
        ],
    },
    "TABS": [],
}

def environment_callback(request):
    """Callback функция для отображения окружения в админке"""
    if DEBUG:
        return "Разработка"
    return "Продакшн"
```

```python
"""
Django settings for ez project.

Generated by 'django-admin startproject' using Django 5.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w+!(#_tbe8^=jq8s@i#l7++rv&zb_$u(z$5i@4+#vc__-88&p*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition



INSTALLED_APPS = [
    'unfold',  # Django Unfold должен быть перед django.contrib.admin
    'unfold.contrib.filters',  # Дополнительные фильтры
    'login',
    'workspace',
    'customers',
    'contractors',
    'equipment',
    'employees',
    'subcontractors',
    'staff.apps.StaffConfig',
    'workspace_control',
    'projects',
    'commercial_proposal',
    'nmacost',
    'itcost',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Для поддержки локализации
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ez.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ← эта строка теперь будет работать
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ez.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/auth/'

# settings.py
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False

# Django Unfold settings
UNFOLD = {
    "SITE_TITLE": "EZ Project Admin",
    "SITE_HEADER": "Административная панель",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_LOGO": None,
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "ez.settings.environment_callback",
    "DASHBOARD_CALLBACK": None,
    "LOGIN": {
        "image": None,
        "redirect_after": None,
    },
    "STYLES": [],
    "SCRIPTS": [],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇳🇱",
                "ru": "🇷🇺",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Главное",
                "separator": True,
                "items": [
                    {
                        "title": "Проекты",
                        "link": "/admin/projects/project/",
                    },
                    {
                        "title": "Коммерческие предложения",
                        "link": "/admin/commercial_proposal/commercialproposal/",
                    },
                    {
                        "title": "Расчеты стоимости",
                        "link": "/admin/itcost/costcalculation/",
                    },
                ],
            },
            {
                "title": "Контакты",
                "separator": True,
                "items": [
                    {
                        "title": "Заказчики",
                        "link": "/admin/customers/customer/",
                    },
                    {
                        "title": "Подрядчики",
                        "link": "/admin/contractors/contractor/",
                    },
                    {
                        "title": "Субподрядчики",
                        "link": "/admin/subcontractors/subcontractor/",
                    },
                    {
                        "title": "Сотрудники",
                        "link": "/admin/employees/employee/",
                    },
                ],
            },
            {
                "title": "Ресурсы",
                "separator": True,
                "items": [
                    {
                        "title": "Оборудование",
                        "link": "/admin/equipment/equipment/",
                    },
                    {
                        "title": "НМА",
                        "link": "/admin/nmacost/nmacost/",
                    },
                ],
            },
            {
                "title": "Система расчета стоимости",
                "separator": True,
                "items": [
                    {
                        "title": "Настройки организации",
                        "link": "/admin/itcost/organizationsettings/",
                    },
                    {
                        "title": "Роли участников",
                        "link": "/admin/itcost/roleassignment/",
                    },
                ],
            },
        ],
    },
    "TABS": [],
}

def environment_callback(request):
    """Callback функция для отображения окружения в админке"""
    if DEBUG:
        return "Разработка"
    return "Продакшн"
```

Система расчета стоимости добавлена в админку. Сделано:

## Добавление системы расчета стоимости в админку

### 1. Улучшенные админ-классы

**CostCalculationAdmin:**
- Отображение: название проекта, заказчик, стоимости (с форматированием), ссылки на связанные НМА и коммерческие предложения
- Поиск: по названию проекта, заказчику, описанию
- Фильтры: по дате создания, создателю, связанным НМА и коммерческим предложениям
- Fieldsets: поля сгруппированы по разделам
- Автозаполнение: `created_by` устанавливается автоматически при создании

**OrganizationSettingsAdmin:**
- Fieldsets: поля сгруппированы логически
- Ограничения: можно создать только одну запись, удаление запрещено

**RoleAssignmentAdmin:**
- Отображение: роль с читаемым названием
- Поиск: по имени пользователя, email
- Автозаполнение: `assigned_by` устанавливается автоматически

### 2. Навигация в Unfold

Добавлены ссылки в боковое меню админки:
- В разделе "Главное": "Расчеты стоимости"
- Новый раздел "Система расчета стоимости":
  - Настройки организации
  - Роли участников

### 3. Дополнительные возможности

- Форматирование денежных значений с разделителями тысяч
- Ссылки на связанные объекты (НМА и коммерческие предложения)
- Raw ID fields для быстрого выбора связанных объектов
- Readonly fields для автоматически рассчитываемых полей

Система расчета стоимости доступна в админке Django Unfold. Модели можно просматривать, редактировать и управлять ими через административный интерфейс.

---

**User**

Добавь функцию удаления проекта из вкладки расчет стоимости проекта

---

**Cursor**

Добавляю функцию удаления расчета стоимости проекта: view, URL и кнопки удаления в шаблонах.


Изучаю примеры удаления и добавляю функцию удаления для расчетов стоимости:


Добавляю функцию удаления: view, URL, шаблон подтверждения и кнопки удаления.


```python
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
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'nma_cost' in form_data:
                        form_data.pop('nma_cost', None)
            else:
                # Удаляем поле, если не выбрано
                if 'nma_cost' in form_data:
                    form_data.pop('nma_cost', None)
        else:
            # Удаляем поле, если не используется
            if 'nma_cost' in form_data:
                form_data.pop('nma_cost', None)
        
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
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'commercial_proposal' in form_data:
                        form_data.pop('commercial_proposal', None)
            else:
                # Удаляем поле, если не выбрано
                if 'commercial_proposal' in form_data:
                    form_data.pop('commercial_proposal', None)
        else:
            # Удаляем поле, если не используется
            if 'commercial_proposal' in form_data:
                form_data.pop('commercial_proposal', None)
        
        # Создаем форму с обновленными данными
        # QueryDict уже обработан выше, пустые значения удалены
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

```python
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
        elif form_data.get("nma_source") == "existing":
            nma_id = form_data.get("existing_nma")
            if nma_id and nma_id != '' and nma_id != 'None':
                try:
                    from nmacost.models import NMACost
                    nma_cost = NMACost.objects.get(pk=nma_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('nma_cost', [str(nma_cost.pk)])
                except (NMACost.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'nma_cost' in form_data:
                        form_data.pop('nma_cost', None)
            else:
                # Удаляем поле, если не выбрано
                if 'nma_cost' in form_data:
                    form_data.pop('nma_cost', None)
        else:
            # Удаляем поле, если не используется
            if 'nma_cost' in form_data:
                form_data.pop('nma_cost', None)
        
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
        elif form_data.get("commercial_source") == "existing":
            commercial_id = form_data.get("existing_commercial")
            if commercial_id and commercial_id != '' and commercial_id != 'None':
                try:
                    from commercial_proposal.models import CommercialProposal
                    commercial_proposal = CommercialProposal.objects.get(pk=commercial_id)
                    # Правильно устанавливаем значение в QueryDict
                    form_data.setlist('commercial_proposal', [str(commercial_proposal.pk)])
                except (CommercialProposal.DoesNotExist, ValueError, TypeError):
                    # Удаляем поле, если значение невалидно
                    if 'commercial_proposal' in form_data:
                        form_data.pop('commercial_proposal', None)
            else:
                # Удаляем поле, если не выбрано
                if 'commercial_proposal' in form_data:
                    form_data.pop('commercial_proposal', None)
        else:
            # Удаляем поле, если не используется
            if 'commercial_proposal' in form_data:
                form_data.pop('commercial_proposal', None)
        
        # Создаем форму с обновленными данными
        # QueryDict уже обработан выше, пустые значения удалены
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
        
        # Добавляем сообщение об ошибках валидации
        if form.errors:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_messages.append(f"{field_label}: {error}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: " + "; ".join(error_messages))
        
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

```

```python
from django.urls import path

from . import views

app_name = "itcost"

urlpatterns = [
    path("", views.CostDashboardView.as_view(), name="dashboard"),
    path(
        "calculations/new/",
        views.CostCalculationCreateView.as_view(),
        name="calculation_create",
    ),
    path(
        "calculations/<int:pk>/",
        views.CostCalculationDetailView.as_view(),
        name="calculation_detail",
    ),
    path(
        "calculations/<int:pk>/edit/",
        views.CostCalculationUpdateView.as_view(),
        name="calculation_edit",
    ),
    path(
        "calculations/<int:pk>/delete/",
        views.CostCalculationDeleteView.as_view(),
        name="calculation_delete",
    ),
    path("settings/", views.OrganizationSettingsUpdateView.as_view(), name="settings"),
    path("roles/", views.RoleAssignmentView.as_view(), name="roles"),
]


```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}Удаление расчета стоимости{% endblock %}

{% block main_content %}
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-danger text-white">
                    <h5 class="mb-0">
                        <i class="fa-solid fa-triangle-exclamation me-2"></i>
                        Подтверждение удаления
                    </h5>
                </div>
                <div class="card-body">
                    <div class="alert alert-warning">
                        <i class="fa-solid fa-exclamation-triangle me-2"></i>
                        <strong>Внимание!</strong> Вы собираетесь удалить расчет стоимости проекта. Это действие нельзя отменить.
                    </div>
                    
                    <h6 class="mb-3">Информация о расчете:</h6>
                    <div class="mb-4">
                        <p><strong>Название проекта:</strong> {{ calculation.project_name }}</p>
                        <p><strong>Заказчик:</strong> {{ calculation.client_name|default:"Не указан" }}</p>
                        <p><strong>Стоимость разработки:</strong> {{ calculation.development_cost|floatformat:2 }} ₽</p>
                        <p><strong>Стоимость НМА:</strong> {{ calculation.intangible_asset_cost|floatformat:2 }} ₽</p>
                        <p><strong>Стоимость коммерческого предложения:</strong> {{ calculation.commercial_offer_cost|floatformat:2 }} ₽</p>
                        <p><strong>Создан:</strong> {{ calculation.created_at|date:"d.m.Y H:i" }}</p>
                        {% if calculation.created_by %}
                            <p><strong>Создал:</strong> {{ calculation.created_by.get_full_name|default:calculation.created_by.username }}</p>
                        {% endif %}
                    </div>
                    
                    <form method="post">
                        {% csrf_token %}
                        <div class="d-flex justify-content-between align-items-center">
                            <a href="{% url 'itcost:calculation_detail' calculation.pk %}" class="btn btn-outline-secondary">
                                <i class="fa-solid fa-arrow-left me-2"></i>Отмена
                            </a>
                            <button type="submit" class="btn btn-danger">
                                <i class="fa-solid fa-trash me-2"></i>Да, удалить расчет
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}{{ calculation.project_name }}{% endblock %}

{% block main_content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3 mb-1">{{ calculation.project_name }}</h1>
            <p class="text-muted mb-0">{{ calculation.client_name|default:"Заказчик не указан" }}</p>
        </div>
        <div class="d-flex gap-2">
            <a href="{% url 'itcost:calculation_edit' calculation.pk %}" class="btn btn-outline-primary">
                <i class="fa-solid fa-pen me-2"></i>Редактировать
            </a>
            <a href="{% url 'itcost:calculation_delete' calculation.pk %}" class="btn btn-outline-danger">
                <i class="fa-solid fa-trash me-2"></i>Удалить
            </a>
            <a href="{% url 'itcost:dashboard' %}" class="btn btn-outline-secondary">К списку</a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ calculation.development_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ calculation.intangible_asset_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость коммерческого предложения</p>
                    <h3 class="fw-bold">{{ calculation.commercial_offer_cost|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Входные данные</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <p class="text-muted mb-1">Трудоемкость</p>
                    <div>{{ calculation.estimated_hours }} ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Ставка</p>
                    <div>{{ calculation.hourly_rate }} ₽/ч</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Инфраструктурные затраты</p>
                    <div>{{ calculation.infrastructure_cost }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Прочие расходы</p>
                    <div>{{ calculation.other_expenses }} ₽</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ calculation.management_overhead_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Риски</p>
                    <div>{{ calculation.risk_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Маржа</p>
                    <div>{{ calculation.profit_margin_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Капитализация НМА</p>
                    <div>{{ calculation.asset_capitalization_percent }}%</div>
                </div>
                <div class="col-md-4">
                    <p class="text-muted mb-1">Наценка КП</p>
                    <div>{{ calculation.commercial_markup_percent }}%</div>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm border-0">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Детализация расчетов</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-6">
                    <p class="text-muted mb-1">Базовая трудоемкость</p>
                    <div>{{ components.base_labor|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Управленческие расходы</p>
                    <div>{{ components.management_overhead|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Риск-резерв</p>
                    <div>{{ components.risk_reserve|floatformat:2 }} ₽</div>
                </div>
                <div class="col-md-6">
                    <p class="text-muted mb-1">Маржа прибыли</p>
                    <div>{{ components.profit_margin|floatformat:2 }} ₽</div>
                </div>
            </div>
            <hr>
            <p class="text-muted mb-1">Описание/ТЗ</p>
            <div>{{ calculation.project_brief|linebreaks|default:"—" }}</div>
        </div>
    </div>

    <!-- Информация о связанных формах -->
    {% if calculation.nma_cost %}
    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Связанная форма НМА</h5>
        </div>
        <div class="card-body">
            <p><strong>Проект:</strong> {{ calculation.nma_cost.project_name }}</p>
            <p><strong>Срок разработки:</strong> {{ calculation.nma_cost.development_period }}</p>
            <p><strong>Итоговая стоимость:</strong> {{ calculation.nma_cost.total_cost|floatformat:2 }} ₽</p>
            <a href="{% url 'nmacost:nmacost-detail' calculation.nma_cost.id %}" class="btn btn-sm btn-outline-primary">
                Открыть форму НМА
            </a>
        </div>
    </div>
    {% endif %}

    {% if calculation.commercial_proposal %}
    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-transparent border-bottom-0">
            <h5 class="mb-0">Связанное коммерческое предложение</h5>
        </div>
        <div class="card-body">
            <p><strong>Название:</strong> {{ calculation.commercial_proposal.title }}</p>
            <p><strong>Заказчик:</strong> {{ calculation.commercial_proposal.customer.name }}</p>
            <p><strong>Итоговая стоимость:</strong> {{ calculation.commercial_proposal.total_cost|floatformat:2 }} ₽</p>
            <a href="{% url 'commercial_proposal:proposal_detail' calculation.commercial_proposal.pk %}" class="btn btn-sm btn-outline-primary">
                Открыть коммерческое предложение
            </a>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}


```

```html
{% extends "itcost/base_with_sidebar.html" %}

{% block title %}Дашборд расчета стоимости{% endblock %}

{% block main_content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3">Система расчета стоимости IT-проекта</h1>
            <p class="text-muted mb-0">Контролируйте ключевые показатели стоимости разработки, НМА и коммерческих предложений.</p>
        </div>
        <div class="d-flex gap-2">
            <a class="btn btn-primary" href="{% url 'itcost:calculation_create' %}">
                <i class="fa-solid fa-plus me-2"></i>Новый расчет
            </a>
            <a class="btn btn-outline-secondary" href="{% url 'itcost:settings' %}">
                <i class="fa-solid fa-gear me-2"></i>Настройки
            </a>
            <a class="btn btn-outline-info" href="{% url 'itcost:roles' %}">
                <i class="fa-solid fa-users me-2"></i>Роли
            </a>
        </div>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Всего проектов</p>
                    <h3 class="fw-bold">{{ metrics.projects_count }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость разработки</p>
                    <h3 class="fw-bold">{{ metrics.development_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Стоимость НМА</p>
                    <h3 class="fw-bold">{{ metrics.intangible_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <p class="text-muted mb-1">Коммерческие предложения</p>
                    <h3 class="fw-bold">{{ metrics.commercial_total|floatformat:2 }} ₽</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Последние расчеты</h5>
                </div>
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead>
                            <tr>
                                <th>Проект</th>
                                <th>Заказчик</th>
                                <th>Разработка</th>
                                <th>НМА</th>
                                <th>Коммерческое</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for calc in calculations %}
                            <tr>
                                <td>
                                    <div class="fw-semibold">{{ calc.project_name }}</div>
                                    <small class="text-muted">обновлено {{ calc.updated_at|date:"d.m.Y H:i" }}</small>
                                </td>
                                <td>{{ calc.client_name|default:"—" }}</td>
                                <td>{{ calc.development_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.intangible_asset_cost|floatformat:2 }} ₽</td>
                                <td>{{ calc.commercial_offer_cost|floatformat:2 }} ₽</td>
                                <td class="text-end">
                                    <div class="btn-group" role="group">
                                        <a href="{% url 'itcost:calculation_detail' calc.pk %}" class="btn btn-sm btn-outline-primary">
                                            <i class="fa-solid fa-eye me-1"></i>Подробнее
                                        </a>
                                        <a href="{% url 'itcost:calculation_delete' calc.pk %}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Вы уверены, что хотите удалить расчет \"{{ calc.project_name }}\"?')">
                                            <i class="fa-solid fa-trash me-1"></i>Удалить
                                        </a>
                                    </div>
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="6" class="text-center py-4 text-muted">Пока нет расчетов. Создайте первый, чтобы увидеть аналитику.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Настройки компании</h5>
                </div>
                <div class="card-body">
                    {% if organization_settings %}
                        <p class="mb-1"><strong>{{ organization_settings.company_name|default:"Название не указано" }}</strong></p>
                        <p class="mb-1 text-muted">{{ organization_settings.director_full_name|default:"Руководитель не указан" }}</p>
                        <p class="mb-1">{{ organization_settings.director_position|default:"Должность не указана" }}</p>
                        <p class="mb-0">
                            <i class="fa-solid fa-phone me-2"></i>{{ organization_settings.contact_phone|default:"—" }}<br>
                            <i class="fa-solid fa-envelope me-2"></i>{{ organization_settings.contact_email|default:"—" }}
                        </p>
                    {% else %}
                        <p class="text-muted mb-0">Настройки еще не заполнены.</p>
                    {% endif %}
                </div>
            </div>

            <div class="card shadow-sm border-0">
                <div class="card-header bg-transparent border-bottom-0">
                    <h5 class="mb-0">Ролевой состав</h5>
                </div>
                <div class="card-body">
                    {% for role in role_breakdown %}
                        <div class="d-flex justify-content-between mb-2">
                            <span>{{ role.label }}</span>
                            <span class="badge bg-primary rounded-pill">{{ role.total }}</span>
                        </div>
                    {% empty %}
                        <p class="text-muted mb-0">Роли еще не назначены.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


```

Добавлена функция удаления расчета стоимости проекта. Реализовано:

## Функция удаления расчета стоимости

### 1. **View для удаления** (`CostCalculationDeleteView`)
- Класс-представление с подтверждением удаления
- Требует авторизации (`LoginRequiredMixin`)
- Показывает страницу подтверждения при GET-запросе
- Удаляет расчет при POST-запросе
- Показывает сообщение об успешном удалении

### 2. **URL маршрут**
- Добавлен путь `/calculations/<int:pk>/delete/`
- Имя маршрута: `calculation_delete`

### 3. **Шаблон подтверждения удаления**
- Страница с предупреждением
- Отображает информацию о расчете (название, заказчик, стоимости, дата создания)
- Кнопки "Отмена" и "Да, удалить расчет"

### 4. **Кнопки удаления в интерфейсе**
- В детальном просмотре: кнопка "Удалить" рядом с "Редактировать"
- В списке на дашборде: кнопка удаления в каждой строке с подтверждением через JavaScript

### Особенности:
- Подтверждение удаления перед выполнением
- Информативное сообщение об успешном удалении
- После удаления перенаправление на дашборд
- Защита от случайного удаления (подтверждение)

Функция удаления доступна в разделе "Система расчета стоимости".

---

**User**

сделай так чтобы приложение Система расчета стоимости IT-проекта
была привязанна к пользователю и не была видна всем поситителям сайьад

