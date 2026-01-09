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
        # Делаем КПП необязательным всегда
        self.fields['kpp'].required = False
        # Убираем все валидаторы из модели, так как валидация происходит в clean_kpp()
        self.fields['kpp'].validators = []

    def clean_kpp(self):
        kpp = self.cleaned_data.get('kpp')
        
        # Если КПП пустой, возвращаем None (валидация формата не требуется)
        if not kpp or not kpp.strip():
            return None
        
        # Если КПП заполнен, проверяем формат (9 цифр)
        kpp = kpp.strip()
        if not kpp.isdigit():
            raise forms.ValidationError('КПП должен содержать только цифры')
        if len(kpp) != 9:
            raise forms.ValidationError('КПП должен содержать 9 цифр')
        
        return kpp

    def clean(self):
        cleaned_data = super().clean()
        contractor_type = cleaned_data.get('contractor_type')
        kpp = cleaned_data.get('kpp')
        
        # Проверка: если выбран ИП, КПП должен быть пустым
        if contractor_type == 'individual':
            if kpp and kpp.strip():
                # Удаляем предыдущие ошибки для КПП, если они были
                if 'kpp' in self._errors:
                    del self._errors['kpp']
                self.add_error('kpp', 'КПП указывается только для юридических лиц')
            # Очищаем КПП для ИП
            cleaned_data['kpp'] = None
        # Если выбрано юридическое лицо, КПП может быть заполнен или пустым - никаких ограничений
        
        return cleaned_data


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