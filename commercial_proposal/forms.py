from django import forms
from .models import CommercialProposal, ServiceItem
from customers.models import Customer

class CommercialProposalForm(forms.ModelForm):
    class Meta:
        model = CommercialProposal
        fields = ['project', 'title', 'customer', 'technical_spec', 'total_cost',
                 'manager_position', 'manager_name', 'manager_email']
        widgets = {
            'project': forms.HiddenInput(),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название коммерческого предложения'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'technical_spec': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Введите техническое задание'
            }),
            'total_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'manager_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите должность менеджера'
            }),
            'manager_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ФИО менеджера'
            }),
            'manager_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
        }
        labels = {
            'title': 'Название',
            'customer': 'Заказчик',
            'technical_spec': 'Техническое задание',
            'total_cost': 'Общая стоимость',
            'manager_position': 'Должность менеджера',
            'manager_name': 'ФИО менеджера',
            'manager_email': 'Email менеджера',
        }

class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = ['name', 'hours', 'start_date', 'end_date', 'cost', 'monthly_cost', 'is_indefinite']
        widgets = {
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
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'monthly_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'is_indefinite': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Название услуги',
            'hours': 'Часы',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'cost': 'Стоимость',
            'monthly_cost': 'Ежемесячная стоимость',
            'is_indefinite': 'Бессрочно',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля необязательными
        self.fields['hours'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        self.fields['cost'].required = False
        self.fields['monthly_cost'].required = False

ServiceItemFormSet = forms.inlineformset_factory(
    CommercialProposal, ServiceItem, form=ServiceItemForm, extra=1, can_delete=True
)