# employees/forms.py
from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'project', 'last_name',
            'first_name',
            'middle_name',
            'position',
            'salary',
            'tax_rate',
            'can_be_shared',
            'is_active'
        ]
        widgets = {
            'project': forms.HiddenInput(),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество (необязательно)'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите должность'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'tax_rate': forms.Select(attrs={
                'class': 'form-select'
            }),
            'can_be_shared': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'position': 'Должность',
            'salary': 'Заработная плата (в месяц)',
            'tax_rate': 'Налоговая ставка',
            'can_be_shared': 'Можно использовать в других проектах',
            'is_active': 'Активный сотрудник',
        }

class EmployeeFilterForm(forms.Form):
    position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по должности'
        }),
        label=''
    )
    active_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Только активные'
    )