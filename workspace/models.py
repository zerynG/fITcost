from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator


class Workspace(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название рабочей области")
    subdomain = models.CharField(
        max_length=50,
        verbose_name='Поддомен',
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_-]+$',
                message='Поддомен может содержать только буквы, цифры, дефисы и подчеркивания'
            )
        ]
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_workspaces',
        verbose_name='Администратор рабочей области'
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Рабочая область"
        verbose_name_plural = "Рабочие области"

    def __str__(self):
        return f"{self.name} ({self.subdomain})"
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete - помечаем как неактивную вместо удаления"""
        self.is_active = False
        self.save()
    
    def hard_delete(self):
        """Физическое удаление объекта"""
        super().delete()


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('completed', 'Завершенный'),
        ('on_hold', 'На паузе'),
        ('cancelled', 'Отменен'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200, verbose_name="Название проекта")
    description = models.TextField(blank=True, verbose_name="Описание проекта")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    deadline = models.DateField(verbose_name="Срок выполнения", null=True, blank=True)
    start_date = models.DateField(verbose_name="Дата начала", null=True, blank=True)
    end_date = models.DateField(verbose_name="Дата окончания", null=True, blank=True)
    
    # Связи с реестрами
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name="Заказчик",
                                 related_name='workspace_projects')
    technical_spec = models.FileField(upload_to='technical_specs/',
                                      null=True, blank=True, verbose_name="Техническое задание")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00,
                                   verbose_name="Налоговая ставка (%)",
                                   validators=[MinValueValidator(0)])

    # Связи с НМА и коммерческим предложением
    nma_cost = models.ForeignKey('nmacost.NMACost', on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name="Расчет НМА",
                                 related_name='workspace_projects')
    commercial_proposal = models.ForeignKey('commercial_proposal.CommercialProposal',
                                           on_delete=models.SET_NULL,
                                           null=True, blank=True,
                                           verbose_name="Коммерческое предложение",
                                           related_name='workspace_projects')

    # Автоматически рассчитываемые поля
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="Итоговая стоимость")
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="Себестоимость")
    cost_with_margin = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                           verbose_name="Стоимость с маржинальностью")
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="Чистая прибыль")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_workspace_projects')

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def calculate_costs(self):
        """
        Расчет стоимости проекта согласно ТЗ:
        - Себестоимость: сумма себестоимостей всех ресурсов
        - Стоимость с маржинальностью: сумма итоговых стоимостей всех ресурсов (если выбран заказчик)
        - Чистая прибыль: сумма (итоговая стоимость - себестоимость) для каждого ресурса
        - Итоговая стоимость: isp = sp + (sp*ns), где sp - стоимость с маржинальностью, ns - налоговая ставка
        """
        from decimal import Decimal
        resources = self.projectresource_set.all()

        # Расчет себестоимости
        self.cost_price = sum(Decimal(str(resource.cost_price)) for resource in resources)

        # Расчет стоимости с маржей (только если выбран заказчик)
        if self.customer:
            self.cost_with_margin = sum(Decimal(str(resource.final_cost)) for resource in resources)
        else:
            self.cost_with_margin = Decimal('0')

        # Расчет чистой прибыли: сумма разниц для каждой услуги
        # p = (i - s) + (i - s) + ... для каждой услуги
        self.net_profit = sum(
            Decimal(str(resource.final_cost)) - Decimal(str(resource.cost_price))
            for resource in resources
        )

        # Расчет итоговой стоимости с налогом: isp = sp + (sp*ns)
        # где isp - итоговая стоимость проекта, sp - стоимость с маржинальностью, ns - налоговая ставка
        if self.cost_with_margin > 0:
            tax_amount = self.cost_with_margin * (self.tax_rate / Decimal('100'))
            self.total_cost = self.cost_with_margin + tax_amount
        else:
            self.total_cost = Decimal('0')

        self.save()

    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Владелец'),
        ('admin', 'Администратор'),
        ('member', 'Участник'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('workspace', 'user')
        verbose_name = "Участник рабочей области"
        verbose_name_plural = "Участники рабочих областей"

    def __str__(self):
        return f"{self.user.username} - {self.workspace.name}"


class ProjectResource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('employee', 'Сотрудник'),
        ('contractor', 'Исполнитель'),
        ('subcontractor', 'Субподрядчик'),
        ('equipment', 'Оборудование'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='projectresource_set')
    name = models.CharField(max_length=200, verbose_name="Название ресурса")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES,
                                     verbose_name="Тип ресурса")

    # Ссылки на различные типы ресурсов
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name="Сотрудник",
                                 related_name='workspace_project_resources')
    contractor = models.ForeignKey('contractors.Contractor', on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name="Исполнитель",
                                   related_name='workspace_project_resources')
    subcontractor = models.ForeignKey('subcontractors.Subcontractor', on_delete=models.SET_NULL,
                                      null=True, blank=True, verbose_name="Субподрядчик",
                                      related_name='workspace_project_resources')
    equipment = models.ForeignKey('equipment.Equipment', on_delete=models.SET_NULL,
                                  null=True, blank=True, verbose_name="Оборудование",
                                  related_name='workspace_project_resources')

    # Услуга исполнителя (для типа "Исполнитель")
    service = models.ForeignKey('contractors.Service', on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name="Услуга исполнителя",
                                related_name='workspace_project_resources')

    service_name = models.CharField(max_length=200, verbose_name="Название услуги")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1,
                                   verbose_name="Количество")
    margin = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                 verbose_name="Маржинальность (%)",
                                 validators=[MinValueValidator(0)])

    # Для субподрядчиков: стоимость за единицу (если не указана в реестре)
    subcontractor_rate = models.DecimalField(max_digits=10, decimal_places=2,
                                             null=True, blank=True,
                                             verbose_name="Стоимость за единицу (для субподрядчика)")

    # Автоматически рассчитываемые поля
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="Себестоимость")
    final_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="Итоговая стоимость")

    def calculate_costs(self):
        """
        Расчет себестоимости и итоговой стоимости ресурса.
        Итоговая стоимость: i = s * m, где i - итоговая стоимость, s - себестоимость, m - маржинальность в виде множителя
        """
        from decimal import Decimal

        base_cost = Decimal('0')

        if self.resource_type == 'employee' and self.employee:
            # Для сотрудников: используем calculate_work_cost или calculate_daily_rate
            # Упрощенный расчет: используем среднее количество рабочих дней в месяце (22)
            working_days_per_month = 22
            daily_rate = self.employee.calculate_daily_rate(working_days_per_month)
            
            # Рассчитываем количество дней в интервале
            days_count = (self.end_date - self.start_date).days + 1
            base_cost = daily_rate * Decimal(str(days_count))

        elif self.resource_type == 'contractor' and self.contractor:
            # Для исполнителей: используем услугу или default_rate
            if self.service:
                # Используем услугу
                rate = self.service.rate
                unit_type = self.service.unit
                base_cost = self.contractor.calculate_cost(
                    self.quantity,
                    rate=rate,
                    unit_type=unit_type
                )
            elif self.contractor.default_rate and self.contractor.default_unit:
                # Используем default_rate
                base_cost = self.contractor.calculate_cost(
                    self.quantity,
                    rate=self.contractor.default_rate,
                    unit_type=self.contractor.default_unit
                )
            else:
                base_cost = Decimal('0')

        elif self.resource_type == 'subcontractor' and self.subcontractor:
            # Для субподрядчиков: используем subcontractor_rate или фиксированную стоимость
            if self.subcontractor_rate:
                # Рассчитываем количество дней
                days_count = (self.end_date - self.start_date).days + 1
                base_cost = Decimal(str(self.subcontractor_rate)) * Decimal(str(days_count))
            else:
                # Если не указана ставка, стоимость = 0
                base_cost = Decimal('0')

        elif self.resource_type == 'equipment' and self.equipment:
            # Для оборудования: используем calculate_service_cost
            base_cost = self.equipment.calculate_service_cost(self.quantity)

        self.cost_price = base_cost

        # Расчет итоговой стоимости с маржинальностью: i = s * m
        # где m = 1 + (margin / 100)
        margin_multiplier = Decimal('1') + (self.margin / Decimal('100'))
        self.final_cost = base_cost * margin_multiplier

        self.save()

    def get_executor_display(self):
        """Возвращает отображаемое имя исполнителя в зависимости от типа ресурса"""
        if self.resource_type == 'employee' and self.employee:
            return self.employee.get_full_name()
        elif self.resource_type == 'contractor' and self.contractor:
            return str(self.contractor)
        elif self.resource_type == 'subcontractor' and self.subcontractor:
            return str(self.subcontractor)
        elif self.resource_type == 'equipment' and self.equipment:
            return str(self.equipment)
        return "-"

    def __str__(self):
        return f"{self.name} - {self.project.name}"