from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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
        
        # Если подключена форма НМА, используем её стоимость, иначе расчетное значение
        if self.nma_cost and self.nma_cost.total_cost:
            self.intangible_asset_cost = self.nma_cost.total_cost
        else:
            self.intangible_asset_cost = components["intangible_asset"]
        
        # Если подключено коммерческое предложение, используем его стоимость, иначе расчетное значение
        if self.commercial_proposal and self.commercial_proposal.total_cost:
            self.commercial_offer_cost = self.commercial_proposal.total_cost
        else:
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


# Сигналы для автоматического обновления значений в CostCalculation при изменении связанных форм
@receiver(post_save, sender='nmacost.NMACost')
def update_calculations_on_nma_change(sender, instance, **kwargs):
    """Обновляет связанные расчеты при изменении НМА."""
    from .models import CostCalculation
    for calculation in CostCalculation.objects.filter(nma_cost=instance):
        calculation.save()


@receiver(post_save, sender='commercial_proposal.CommercialProposal')
def update_calculations_on_commercial_change(sender, instance, **kwargs):
    """Обновляет связанные расчеты при изменении коммерческого предложения."""
    from .models import CostCalculation
    for calculation in CostCalculation.objects.filter(commercial_proposal=instance):
        calculation.save()

