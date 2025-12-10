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
            'project': forms.HiddenInput(),  # Скрытое поле, устанавливается автоматически
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'acquisition_type': forms.Select(attrs={'class': 'form-control'}),
            'operational_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'service_cost_per_unit': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'acquisition_type': 'Тип приобретения',
            'operational_cost': 'Эксплуатационная стоимость',
            'unit': 'Единица измерения',
            'service_cost_per_unit': 'Стоимость услуг за единицу',
        }

    def clean(self):
        cleaned_data = super().clean()
        acquisition_type = cleaned_data.get('acquisition_type')
        operational_cost = cleaned_data.get('operational_cost')
        service_cost = cleaned_data.get('service_cost_per_unit')

        if acquisition_type == 'rent':
            if not operational_cost:
                self.add_error('operational_cost',
                               'Для арендованного оборудования необходимо указать эксплуатационную стоимость')
            elif service_cost and operational_cost > service_cost:
                self.add_error('service_cost_per_unit',
                               'Стоимость услуг не может быть ниже эксплуатационной стоимости для арендованного оборудования')

        return cleaned_data