from django import forms
from django.utils import timezone
from .models import Project, Workspace, WorkspaceMember
from django.contrib.auth.models import User


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ['name', 'subdomain', 'admin', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название рабочей области'
            }),
            'subdomain': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите поддомен'
            }),
            'admin': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Введите описание'
            }),
        }
        labels = {
            'name': 'Название рабочей области',
            'subdomain': 'Поддомен',
            'admin': 'Администратор',
            'description': 'Описание',
        }

    def clean_subdomain(self):
        subdomain = self.cleaned_data.get('subdomain')
        if Workspace.objects.filter(subdomain__iexact=subdomain, is_active=True).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Рабочая область с таким поддоменом уже существует')
        return subdomain


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'deadline', 'start_date', 'end_date', 'customer', 'tax_rate']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название проекта'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Введите описание проекта'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
        }
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
            'status': 'Статус',
            'deadline': 'Срок выполнения',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'customer': 'Заказчик',
            'tax_rate': 'Налоговая ставка (%)',
        }

    def clean_end_date(self):
        """Проверяем, что дата окончания проекта еще не наступила"""
        end_date = self.cleaned_data.get('end_date')
        if end_date:
            today = timezone.now().date()
            if end_date < today:
                raise forms.ValidationError('Дата окончания проекта не может быть в прошлом. Проект уже завершен.')
        return end_date


class WorkspaceMemberForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Пользователь",
        widget=forms.Select()
    )

    class Meta:
        model = WorkspaceMember
        fields = ['user', 'role']
        labels = {
            'role': 'Роль',
        }