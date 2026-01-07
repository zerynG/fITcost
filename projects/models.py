from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Project(models.Model):
    RESOURCE_TYPES = [
        ('employee', 'Сотрудник'),
        ('contractor', 'Исполнитель'),
        ('subcontractor', 'Субподрядчик'),
        ('equipment', 'Оборудование'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название проекта")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    description = models.TextField(verbose_name="Описание проекта", blank=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name="Заказчик",
                                 related_name='legacy_projects')
    technical_spec = models.FileField(upload_to='technical_specs/',
                                      null=True, blank=True, verbose_name="Техническое задание")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00,
                                   verbose_name="Налоговая ставка (%)",
                                   validators=[MinValueValidator(0)])

    # Связи с НМА и коммерческим предложением
    nma_cost = models.ForeignKey('nmacost.NMACost', on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name="Расчет НМА",
                                 related_name='legacy_projects')
    commercial_proposal = models.ForeignKey('commercial_proposal.CommercialProposal',
                                           on_delete=models.SET_NULL,
                                           null=True, blank=True,
                                           verbose_name="Коммерческое предложение",
                                           related_name='legacy_projects')

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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def calculate_costs(self):
        """
        Расчет стоимости проекта согласно ТЗ:
        - Себестоимость: сумма себестоимостей всех ресурсов
        - Стоимость с маржинальностью: сумма итоговых стоимостей всех ресурсов (если выбран заказчик)
        - Чистая прибыль: сумма (итоговая стоимость - себестоимость) для каждого ресурса
        - Итоговая стоимость проекта: простая сумма итоговых стоимостей всех ресурсов (без налога и других переменных)
        """
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

        # Итоговая стоимость проекта: простая сумма итоговых стоимостей всех ресурсов (без налога и других переменных)
        self.total_cost = sum(Decimal(str(resource.final_cost)) for resource in resources)

        self.save()

    def __str__(self):
        return self.name


class ProjectResource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('employee', 'Сотрудник'),
        ('contractor', 'Исполнитель'),
        ('subcontractor', 'Субподрядчик'),
        ('equipment', 'Оборудование'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name="Название ресурса")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES,
                                     verbose_name="Тип ресурса")

    # Ссылки на различные типы ресурсов
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name="Сотрудник")
    contractor = models.ForeignKey('contractors.Contractor', on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name="Исполнитель")
    subcontractor = models.ForeignKey('subcontractors.Subcontractor', on_delete=models.SET_NULL,
                                      null=True, blank=True, verbose_name="Субподрядчик")
    equipment = models.ForeignKey('equipment.Equipment', on_delete=models.SET_NULL,
                                  null=True, blank=True, verbose_name="Оборудование")

    # Услуга исполнителя (для типа "Исполнитель")
    service = models.ForeignKey('contractors.Service', on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name="Услуга исполнителя")

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
        from datetime import timedelta

        base_cost = Decimal('0')

        if self.resource_type == 'employee' and self.employee:
            # Для сотрудников: используем calculate_work_cost или calculate_daily_rate
            # Упрощенный расчет: используем среднее количество рабочих дней в месяце (22)
            working_days_per_month = 22
            daily_rate = self.employee.calculate_daily_rate(working_days_per_month)

            # Рассчитываем количество дней в интервале
            days_count = (self.end_date - self.start_date).days + 1
            # calculate_daily_rate теперь возвращает Decimal, не нужно преобразовывать
            base_cost = daily_rate * Decimal(str(days_count))

        elif self.resource_type == 'contractor' and self.contractor:
            # Для исполнителей: используем услугу или default_rate
            if self.service:
                # Используем услугу
                rate = self.service.rate
                unit_type = self.service.unit
                # calculate_cost теперь возвращает Decimal, не нужно преобразовывать
                base_cost = self.contractor.calculate_cost(
                    self.quantity,
                    rate=rate,
                    unit_type=unit_type
                )
            elif self.contractor.default_rate and self.contractor.default_unit:
                # Используем default_rate
                # calculate_cost теперь возвращает Decimal, не нужно преобразовывать
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
            # Передаем quantity как Decimal для корректных вычислений
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