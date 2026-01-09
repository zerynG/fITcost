from django import forms
from .models import Equipment


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'project', 'name', 'description', 'acquisition_type',
            'operational_cost', 'unit', 'service_cost_per_unit', 'can_be_shared'
        ]
        widgets = {
            'project': forms.HiddenInput(),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название оборудования'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите описание оборудования'
            }),
            'acquisition_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'operational_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'service_cost_per_unit': forms.NumberInput(attrs={
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
            'name': 'Название',
            'description': 'Описание',
            'acquisition_type': 'Тип приобретения',
            'operational_cost': 'Эксплуатационная стоимость',
            'unit': 'Единица измерения',
            'service_cost_per_unit': 'Стоимость услуг за единицу',
            'can_be_shared': 'Можно использовать в других проектах',
        }

    def clean(self):
        # Ограничения по эксплуатационной стоимости и стоимости услуг за единицу убраны
        cleaned_data = super().clean()
        return cleaned_data