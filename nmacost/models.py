from django.db import models
from django.contrib.auth.models import User


class NMACost(models.Model):
    project = models.OneToOneField(
        'workspace.Project',
        on_delete=models.CASCADE,
        related_name='nma_cost_entry',
        null=True,
        blank=True,
        verbose_name='Проект'
    )
    development_period = models.CharField(max_length=100, verbose_name="Срок разработки")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Итоговая стоимость", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Стоимость НМА"
        verbose_name_plural = "Стоимости НМА"

    def __str__(self):
        project_name = self.project.name if self.project else "Без проекта"
        return f"НМА: {project_name} - {self.total_cost} руб."


class ResourceItem(models.Model):
    nmacost = models.ForeignKey(NMACost, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200, verbose_name="Наименование ресурса")
    description = models.TextField(verbose_name="Описание", blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    unit = models.CharField(max_length=50, verbose_name="Единица измерения")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость за единицу")
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Общая стоимость")

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"

    def __str__(self):
        return f"{self.name} - {self.total_cost} руб."

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем общую стоимость
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)