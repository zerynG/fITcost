from django import forms
from .models import NMACost, ResourceItem

class NMACostForm(forms.ModelForm):
    class Meta:
        model = NMACost
        fields = ['project', 'development_period']
        widgets = {
            'project': forms.HiddenInput(),  # Скрытое поле, устанавливается автоматически
            'development_period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 3 месяца'
            }),
        }
        labels = {
            'project': 'Проект',
            'development_period': 'Срок разработки',
        }

class ResourceItemForm(forms.ModelForm):
    class Meta:
        model = ResourceItem
        fields = ['name', 'description', 'quantity', 'unit', 'unit_cost']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Наименование ресурса'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание ресурса'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'шт., час, день и т.д.'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
        }
        labels = {
            'name': 'Наименование',
            'description': 'Описание',
            'quantity': 'Количество',
            'unit': 'Единица измерения',
            'unit_cost': 'Стоимость за единицу',
        }