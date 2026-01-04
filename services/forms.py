from django import forms
from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['project', 'name', 'hours', 'cost', 'start_date', 'end_date', 'monthly_cost', 'is_indefinite']
        widgets = {
            'project': forms.HiddenInput(),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название услуги'
            }),
            'hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0',
                'placeholder': '0.0'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_end_date'
            }),
            'monthly_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'is_indefinite': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_indefinite',
                'onchange': 'toggleEndDate()'
            }),
        }
        labels = {
            'name': 'Название услуги',
            'hours': 'Часы',
            'cost': 'Стоимость',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'monthly_cost': 'Ежемесячная стоимость',
            'is_indefinite': 'Бессрочно',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля необязательными
        self.fields['hours'].required = False
        self.fields['cost'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        self.fields['monthly_cost'].required = False

    def clean(self):
        cleaned_data = super().clean()
        is_indefinite = cleaned_data.get('is_indefinite', False)
        end_date = cleaned_data.get('end_date')

        # Если бессрочно, очищаем end_date
        if is_indefinite:
            cleaned_data['end_date'] = None
        # Если не бессрочно и end_date не указан, не делаем его обязательным
        # (пользователь может указать позже или оставить пустым)

        return cleaned_data

