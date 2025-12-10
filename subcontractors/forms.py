from django import forms
from .models import Subcontractor


class SubcontractorForm(forms.ModelForm):
    class Meta:
        model = Subcontractor
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),  # Скрытое поле, устанавливается автоматически
            'legal_address': forms.Textarea(attrs={'rows': 3}),
            'actual_address': forms.Textarea(attrs={'rows': 3}),
            'contractor_type': forms.RadioSelect(),
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
        label='Тип контрагента'
    )
    is_active = forms.ChoiceField(
        choices=[('', 'Все'), ('true', 'Активные'), ('false', 'Неактивные')],
        required=False,
        label='Статус'
    )
    search = forms.CharField(required=False, label='Поиск')