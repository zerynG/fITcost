from django import forms
from .models import Subcontractor


class SubcontractorForm(forms.ModelForm):
    class Meta:
        model = Subcontractor
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите наименование'
            }),
            'contractor_type': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'inn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ИНН'
            }),
            'kpp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите КПП'
            }),
            'ogrn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ОГРН'
            }),
            'legal_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите юридический адрес'
            }),
            'actual_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите фактический адрес'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'director_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ФИО директора'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название банка'
            }),
            'bank_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите расчетный счет'
            }),
            'corr_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите корреспондентский счет'
            }),
            'bik': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите БИК'
            }),
            'can_be_shared': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем КПП необязательным при создании
        if not self.instance.pk:
            self.fields['kpp'].required = False


class SubcontractorFilterForm(forms.Form):
    contractor_type = forms.ChoiceField(
        choices=[('', 'Все типы')] + Subcontractor.CONTRACTOR_TYPE_CHOICES,
        required=False,
        label='Тип контрагента',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.ChoiceField(
        choices=[('', 'Все'), ('true', 'Активные'), ('false', 'Неактивные')],
        required=False,
        label='Статус',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по названию, ИНН, email...'
        })
    )