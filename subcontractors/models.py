from django.db import models
from django.core.validators import RegexValidator


class Subcontractor(models.Model):
    CONTRACTOR_TYPE_CHOICES = [
        ('legal', 'Юридическое лицо'),
        ('individual', 'Индивидуальный предприниматель'),
    ]

    project = models.ForeignKey(
        'workspace.Project',
        on_delete=models.CASCADE,
        related_name='subcontractors',
        null=True,
        blank=True,
        verbose_name='Проект'
    )
    name = models.CharField(max_length=255, verbose_name='Наименование')
    contractor_type = models.CharField(
        max_length=20,
        choices=CONTRACTOR_TYPE_CHOICES,
        verbose_name='Тип контрагента'
    )
    inn = models.CharField(
        max_length=12,
        unique=False,  # Убираем unique, так как может быть в разных проектах
        verbose_name='ИНН',
        validators=[RegexValidator(r'^\d{10,12}$', 'ИНН должен содержать 10 или 12 цифр')]
    )
    kpp = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        verbose_name='КПП',
        # Валидатор убран, так как валидация происходит в форме
    )
    ogrn = models.CharField(
        max_length=15,
        verbose_name='ОГРН/ОГРНИП',
        validators=[RegexValidator(r'^\d{13,15}$', 'ОГРН должен содержать 13 или 15 цифр')]
    )
    legal_address = models.TextField(verbose_name='Юридический адрес')
    actual_address = models.TextField(verbose_name='Фактический адрес')
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        validators=[RegexValidator(r'^\+?[1-9]\d{0,19}$', 'Введите корректный номер телефона')]
    )
    email = models.EmailField(verbose_name='Email')
    director_name = models.CharField(max_length=255, verbose_name='ФИО руководителя')
    bank_name = models.CharField(max_length=255, verbose_name='Наименование банка')
    bank_account = models.CharField(max_length=20, verbose_name='Расчетный счет')
    corr_account = models.CharField(max_length=20, verbose_name='Корреспондентский счет')
    bik = models.CharField(
        max_length=9,
        verbose_name='БИК',
        validators=[RegexValidator(r'^\d{9}$', 'БИК должен содержать 9 цифр')]
    )
    can_be_shared = models.BooleanField(
        default=False,
        verbose_name='Можно использовать в других проектах'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Субподрядчик'
        verbose_name_plural = 'Субподрядчики'
        ordering = ['name']
        unique_together = [('project', 'inn')]  # ИНН должен быть уникальным в рамках проекта

    def __str__(self):
        return f"{self.name} ({self.get_contractor_type_display()})"

    def save(self, *args, **kwargs):
        # Для ИП очищаем КПП
        if self.contractor_type == 'individual':
            self.kpp = None
        super().save(*args, **kwargs)