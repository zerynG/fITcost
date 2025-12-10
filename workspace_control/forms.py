from django import forms
from .models import Workspace, WorkspaceMember
from django.contrib.auth.models import User


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ['name', 'subdomain', 'admin']
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
        }
        labels = {
            'name': 'Название рабочей области',
            'subdomain': 'Поддомен',
            'admin': 'Администратор',
        }

    def clean_subdomain(self):
        subdomain = self.cleaned_data.get('subdomain')
        if Workspace.objects.filter(subdomain__iexact=subdomain).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Рабочая область с таким поддоменом уже существует')
        return subdomain


class WorkspaceMemberForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Пользователь'
    )

    class Meta:
        model = WorkspaceMember
        fields = ['user', 'permission']
        widgets = {
            'permission': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'permission': 'Права доступа',
        }