from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['project', 'inn', 'customer_type', 'name', 'full_name', 'email', 'phone', 'can_be_shared']
        widgets = {
            'project': forms.HiddenInput(),  # Скрытое поле, устанавливается автоматически
        }
        widgets = {
            'inn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ИНН'
            }),
            'customer_type': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'toggleCompanyName()'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название',
                'id': 'company-name-field'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ФИО'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите телефон'
            }),
            'can_be_shared': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_inn(self):
        inn = self.cleaned_data.get('inn')
        project = self.cleaned_data.get('project')
        # Проверка на уникальность ИНН в рамках проекта
        if project:
            if Customer.objects.filter(inn=inn, project=project).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Заказчик с таким ИНН уже существует в этом проекте')
        return inn