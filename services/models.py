from django.db import models
from django.core.exceptions import ValidationError


class Service(models.Model):
    """Модель услуги в реестре услуг"""
    project = models.ForeignKey(
        'workspace.Project',
        on_delete=models.CASCADE,
        related_name='services',
        null=True,
        blank=True,
        verbose_name='Проект'
    )
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Часы",
        blank=True,
        null=True
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость",
        blank=True,
        null=True
    )
    start_date = models.DateField(
        verbose_name="Дата начала",
        blank=True,
        null=True
    )
    end_date = models.DateField(
        verbose_name="Дата окончания",
        blank=True,
        null=True
    )
    monthly_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ежемесячная стоимость",
        blank=True,
        null=True
    )
    is_indefinite = models.BooleanField(
        default=False,
        verbose_name="Бессрочно"
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def clean(self):
        """Валидация: если бессрочно, end_date должен быть пустым"""
        if self.is_indefinite and self.end_date:
            raise ValidationError({
                'end_date': 'Дата окончания не должна быть указана для бессрочных услуг'
            })

    def save(self, *args, **kwargs):
        # Очищаем end_date если услуга бессрочная
        if self.is_indefinite:
            self.end_date = None
        self.full_clean()
        super().save(*args, **kwargs)

