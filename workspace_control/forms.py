from django import forms
from .models import Workspace, WorkspaceMember
from django.contrib.auth.models import User


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ['name', 'subdomain', 'admin']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subdomain': forms.TextInput(attrs={'class': 'form-control'}),
            'admin': forms.Select(attrs={'class': 'form-control'}),
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
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Пользователь'
    )

    class Meta:
        model = WorkspaceMember
        fields = ['user', 'permission']
        widgets = {
            'permission': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'permission': 'Права доступа',
        }