from django.db import models


class Contractor(models.Model):
    CONTRACTOR_TYPE_CHOICES = [
        ('GPH', 'ГПХ'),
        ('NPD', 'НПД'),
    ]
    UNIT_CHOICES = [
        ('hours', 'Часы'),
        ('days', 'Дни'),
        ('fixed', 'Полная стоимость'),
    ]

    project = models.ForeignKey(
        'workspace.Project',
        on_delete=models.CASCADE,
        related_name='contractors',
        null=True,
        blank=True,
        verbose_name='Проект'
    )
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отчество')
    contract_type = models.CharField(
        max_length=3,
        choices=CONTRACTOR_TYPE_CHOICES,
        verbose_name='Тип оформления'
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Налоговая ставка (%)'
    )
    # Поля по умолчанию (если не создавать отдельную услугу)
    default_unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        blank=True,
        null=True,
        verbose_name='Единица измерения'
    )
    default_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Стоимость за единицу'
    )
    can_be_shared = models.BooleanField(
        default=False,
        verbose_name='Можно использовать в других проектах'
    )

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def calculate_cost(self, unit_count, rate=None, unit_type=None):
        """
        Расчет стоимости услуг исполнителя.
        su = ((cez * suz) + ((cez * suz) * ns))
        """
        from decimal import Decimal
        
        # Преобразуем все значения в Decimal для корректных вычислений
        unit_count = Decimal(str(unit_count))
        
        if rate is None:
            rate = self.default_rate
        if rate is None:
            return Decimal('0')
        
        rate = Decimal(str(rate))
        if unit_type is None:
            unit_type = self.default_unit

        base_cost = unit_count * rate

        # Налоговая ставка применяется только для ГПХ
        if self.contract_type == 'GPH':
            tax_multiplier = self.tax_rate / Decimal('100')
            total_cost = base_cost + (base_cost * tax_multiplier)
        else:
            total_cost = base_cost

        return total_cost


class Service(models.Model):
    UNIT_CHOICES = [
        ('hours', 'Часы'),
        ('days', 'Дни'),
        ('fixed', 'Полная стоимость'),
    ]

    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='Исполнитель'
    )
    name = models.CharField(max_length=200, verbose_name='Наименование услуги')
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        verbose_name='Единица измерения'
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость за единицу'
    )

    class Meta:
        verbose_name = 'Услуга исполнителя'
        verbose_name_plural = 'Услуги исполнителей'

    def __str__(self):
        return f"{self.name} ({self.contractor})"