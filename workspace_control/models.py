from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Workspace(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'Просмотр'),
        ('edit', 'Редактирование проектов'),
        ('admin', 'Администратор'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название рабочей области')
    subdomain = models.CharField(
        max_length=50,
        verbose_name='Поддомен',
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_-]+$',
                message='Поддомен может содержать только буквы, цифры, дефисы и подчеркивания'
            )
        ]
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_control_workspaces',
        verbose_name='Администратор рабочей области'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Рабочая область Control'
        verbose_name_plural = 'Рабочие области Control'

    def __str__(self):
        return f"{self.name} ({self.subdomain})"


class WorkspaceMember(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='control_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='control_workspace_memberships')
    permission = models.CharField(max_length=20, choices=Workspace.PERMISSION_CHOICES, default='view')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['workspace', 'user']
        verbose_name = 'Участник рабочей области'
        verbose_name_plural = 'Участники рабочих областей'

    def __str__(self):
        return f"{self.user.username} - {self.workspace.name}"