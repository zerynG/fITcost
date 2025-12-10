from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['project', 'inn', 'customer_type', 'name', 'full_name', 'email', 'phone', 'can_be_shared']
        widgets = {
            'project': forms.HiddenInput(),
            'inn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ИНН'
            }),
            'customer_type': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'toggleCompanyName()'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название организации',
                'id': 'company-name-field'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ФИО'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
            'can_be_shared': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'inn': 'ИНН',
            'customer_type': 'Тип заказчика',
            'name': 'Название организации',
            'full_name': 'ФИО',
            'email': 'Email',
            'phone': 'Телефон',
            'can_be_shared': 'Можно использовать в других проектах',
        }

    def clean_inn(self):
        inn = self.cleaned_data.get('inn')
        project = self.cleaned_data.get('project')
        # Проверка на уникальность ИНН в рамках проекта
        if project:
            if Customer.objects.filter(inn=inn, project=project).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Заказчик с таким ИНН уже существует в этом проекте')
        return inn