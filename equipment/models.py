from django.db import models


class Equipment(models.Model):
    ACQUISITION_TYPES = [
        ('own', 'Собственное'),
        ('rent', 'В аренде'),
    ]

    UNIT_TYPES = [
        ('hours', 'Часы'),
        ('days', 'Дни'),
        ('full', 'Полная стоимость'),
    ]

    project = models.ForeignKey(
        'workspace.Project',
        on_delete=models.CASCADE,
        related_name='equipment',
        null=True,
        blank=True,
        verbose_name='Проект'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True)
    acquisition_type = models.CharField(
        max_length=10,
        choices=ACQUISITION_TYPES,
        verbose_name='Тип приобретения'
    )
    operational_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Эксплуатационная стоимость',
        null=True,
        blank=True
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_TYPES,
        verbose_name='Единица измерения'
    )
    service_cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость услуг за единицу измерения'
    )
    can_be_shared = models.BooleanField(
        default=False,
        verbose_name='Можно использовать в других проектах'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.acquisition_type == 'rent' and not self.operational_cost:
            raise ValidationError({
                'operational_cost': 'Для арендованного оборудования необходимо указать эксплуатационную стоимость'
            })
        if self.acquisition_type == 'rent' and self.operational_cost is not None and self.service_cost_per_unit is not None:
            if self.operational_cost < self.service_cost_per_unit:
                raise ValidationError({
                    'service_cost_per_unit': 'Стоимость услуг не может быть ниже эксплуатационной стоимости для арендованного оборудования'
                })

    def calculate_service_cost(self, quantity):
        """Расчет стоимости услуг"""
        from decimal import Decimal
        # Преобразуем quantity в Decimal для корректного умножения
        quantity_decimal = Decimal(str(quantity))
        return quantity_decimal * self.service_cost_per_unit


    @classmethod
    def get_active_count(cls):
        """Возвращает количество активных инструментов"""
        return cls.objects.filter(is_active=True).count()

        # остальные методы модели...