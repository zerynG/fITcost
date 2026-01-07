from django.db import models
from customers.models import Customer  # Предполагая, что у вас есть модель Customer
from django.conf import settings


class CommercialProposal(models.Model):
    project = models.ForeignKey(
        'workspace.Project',
        on_delete=models.CASCADE,
        related_name='commercial_proposals',
        null=True,
        blank=True,
        verbose_name='Проект'
    )
    title = models.CharField(max_length=200, verbose_name="Название документа")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Заказчик")
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата формирования")
    technical_spec = models.TextField(verbose_name="Техническое задание")
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Итоговая стоимость")
    manager_position = models.CharField(max_length=100, verbose_name="Должность руководителя")
    manager_name = models.CharField(max_length=100, verbose_name="ФИО руководителя")
    manager_email = models.EmailField(verbose_name="Email руководителя")

    class Meta:
        verbose_name = "Коммерческое предложение"
        verbose_name_plural = "Коммерческие предложения"

    def __str__(self):
        return f"{self.title} - {self.customer.name if self.customer else 'Не указан'}"


class ServiceItem(models.Model):
    proposal = models.ForeignKey(CommercialProposal, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    hours = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Количество часов", blank=True, null=True)
    start_date = models.DateField(verbose_name="Дата начала", blank=True, null=True)
    end_date = models.DateField(verbose_name="Дата окончания", blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость", blank=True, null=True)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма в месяц", blank=True, null=True)
    is_indefinite = models.BooleanField(default=False, verbose_name="Бессрочный срок")

    class Meta:
        verbose_name = "Позиция услуги"
        verbose_name_plural = "Позиции услуг"