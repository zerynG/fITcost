from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Employee(models.Model):
    TAX_RATE_CHOICES = [
        ('30.2', '30.2% (стандартная)'),
        ('7.6', '7.6% (льготная)'),
    ]

    project = models.ForeignKey(
        'workspace.Project',
        on_delete=models.CASCADE,
        related_name='employees',
        null=True,
        blank=True,
        verbose_name='Проект'
    )
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отчество')
    position = models.CharField(max_length=200, verbose_name='Должность')
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Заработная плата в месяц',
        validators=[MinValueValidator(0)]
    )
    tax_rate = models.CharField(
        max_length=10,
        choices=TAX_RATE_CHOICES,
        default='30.2',
        verbose_name='Налоговая ставка (%)'
    )
    can_be_shared = models.BooleanField(
        default=False,
        verbose_name='Можно использовать в других проектах'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активный сотрудник')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

    def get_full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    def calculate_daily_rate(self, working_days_in_month):
        """Рассчитывает стоимость одного рабочего дня"""
        from decimal import Decimal
        
        if working_days_in_month <= 0:
            return Decimal('0')
        
        # Используем Decimal для всех вычислений
        base_salary = self.salary  # Уже Decimal
        tax_rate_decimal = Decimal(str(self.tax_rate))
        tax_amount = base_salary * (tax_rate_decimal / Decimal('100'))
        total_cost = base_salary + tax_amount
        working_days = Decimal(str(working_days_in_month))
        return total_cost / working_days

    def calculate_work_cost(self, start_date, end_date, working_days_per_month):
        """
        Рассчитывает стоимость работы за период
        working_days_per_month: словарь {год-месяц: количество рабочих дней}
        """
        from datetime import datetime, timedelta
        from collections import defaultdict
        from decimal import Decimal

        # Группируем дни по месяцам
        monthly_days = defaultdict(int)
        current_date = start_date

        while current_date <= end_date:
            month_key = f"{current_date.year}-{current_date.month:02d}"
            monthly_days[month_key] += 1
            current_date += timedelta(days=1)

        total_cost = Decimal('0')

        for month_key, days_count in monthly_days.items():
            if month_key in working_days_per_month:
                daily_rate = self.calculate_daily_rate(working_days_per_month[month_key])
                # daily_rate теперь Decimal, days_count - int, преобразуем в Decimal
                total_cost += daily_rate * Decimal(str(days_count))

        return total_cost