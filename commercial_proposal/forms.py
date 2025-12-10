from django import forms
from .models import CommercialProposal, ServiceItem
from customers.models import Customer

class CommercialProposalForm(forms.ModelForm):
    class Meta:
        model = CommercialProposal
        fields = ['project', 'title', 'customer', 'technical_spec', 'total_cost',
                 'manager_position', 'manager_name', 'manager_email']
        widgets = {
            'project': forms.HiddenInput(),  # Скрытое поле, устанавливается автоматически
            'technical_spec': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'manager_position': forms.TextInput(attrs={'class': 'form-control'}),
            'manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manager_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = ['name', 'hours', 'start_date', 'end_date', 'cost', 'monthly_cost', 'is_indefinite']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monthly_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_indefinite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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