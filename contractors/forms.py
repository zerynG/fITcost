from django import forms
from .models import Contractor, Service

class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = [
            'project', 'last_name', 'first_name', 'middle_name',
            'contract_type', 'tax_rate',
            'default_unit', 'default_rate', 'can_be_shared'
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
            'contract_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'default_unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'default_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'can_be_shared': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'contract_type': 'Тип оформления',
            'tax_rate': 'Налоговая ставка (%)',
            'default_unit': 'Единица измерения по умолчанию',
            'default_rate': 'Ставка по умолчанию',
            'can_be_shared': 'Можно использовать в других проектах',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем tax_rate необязательным, так как для NPD оно не нужно
        self.fields['tax_rate'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        contract_type = cleaned_data.get('contract_type')
        tax_rate = cleaned_data.get('tax_rate')
        
        # Если выбран NPD, устанавливаем tax_rate в 0
        if contract_type == 'NPD':
            cleaned_data['tax_rate'] = 0
        elif contract_type == 'GPH' and (tax_rate is None or tax_rate == ''):
            # Для ГПХ tax_rate обязателен
            raise forms.ValidationError({
                'tax_rate': 'Налоговая ставка обязательна для типа оформления ГПХ'
            })
        
        return cleaned_data

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'unit', 'rate']
        widgets = {
            'unit': forms.Select(choices=Service.UNIT_CHOICES),
            'rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }