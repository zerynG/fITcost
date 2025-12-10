from django import forms
from .models import Project, ProjectResource
from customers.models import Customer
from employees.models import Employee
from contractors.models import Contractor, Service
from subcontractors.models import Subcontractor
from equipment.models import Equipment


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'start_date', 'end_date', 'description', 'customer',
            'technical_spec', 'tax_rate', 'nma_cost', 'commercial_proposal'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'technical_spec': forms.FileInput(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'nma_cost': forms.Select(attrs={'class': 'form-control'}),
            'commercial_proposal': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка queryset для НМА
        from nmacost.models import NMACost
        self.fields['nma_cost'].queryset = NMACost.objects.all()
        self.fields['nma_cost'].required = False
        
        # Настройка queryset для коммерческого предложения
        from commercial_proposal.models import CommercialProposal
        if self.instance and self.instance.customer:
            self.fields['commercial_proposal'].queryset = CommercialProposal.objects.filter(
                customer=self.instance.customer
            )
        else:
            self.fields['commercial_proposal'].queryset = CommercialProposal.objects.all()
        self.fields['commercial_proposal'].required = False
        
        # Исправление проблемы с датами - устанавливаем правильный формат для HTML5 date input
        if self.instance and self.instance.pk:
            if self.instance.start_date:
                self.fields['start_date'].widget.attrs['value'] = self.instance.start_date.strftime('%Y-%m-%d')
            if self.instance.end_date:
                self.fields['end_date'].widget.attrs['value'] = self.instance.end_date.strftime('%Y-%m-%d')


class ProjectResourceForm(forms.ModelForm):
    # Поля для создания нового ресурса
    create_new_employee = forms.BooleanField(required=False, label="Создать нового сотрудника")
    create_new_contractor = forms.BooleanField(required=False, label="Создать нового исполнителя")
    create_new_subcontractor = forms.BooleanField(required=False, label="Создать нового субподрядчика")
    create_new_equipment = forms.BooleanField(required=False, label="Создать новое оборудование")

    class Meta:
        model = ProjectResource
        fields = [
            'name', 'resource_type', 'employee', 'contractor',
            'subcontractor', 'equipment', 'service', 'service_name',
            'start_date', 'end_date', 'quantity', 'margin', 'subcontractor_rate'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'service_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'margin': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'subcontractor_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка queryset для полей
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)
        self.fields['employee'].required = False
        self.fields['employee'].widget.attrs.update({'class': 'form-control'})

        self.fields['contractor'].queryset = Contractor.objects.all()
        self.fields['contractor'].required = False
        self.fields['contractor'].widget.attrs.update({'class': 'form-control'})

        self.fields['subcontractor'].queryset = Subcontractor.objects.filter(is_active=True)
        self.fields['subcontractor'].required = False
        self.fields['subcontractor'].widget.attrs.update({'class': 'form-control'})

        self.fields['equipment'].queryset = Equipment.objects.filter(is_active=True)
        self.fields['equipment'].required = False
        self.fields['equipment'].widget.attrs.update({'class': 'form-control'})

        self.fields['service'].queryset = Service.objects.all()
        self.fields['service'].required = False
        self.fields['service'].widget.attrs.update({'class': 'form-control'})

        # Если выбран исполнитель, обновляем queryset услуг
        if self.instance and self.instance.contractor:
            self.fields['service'].queryset = Service.objects.filter(contractor=self.instance.contractor)
        elif 'contractor' in self.data and self.data['contractor']:
            try:
                contractor_id = int(self.data['contractor'])
                self.fields['service'].queryset = Service.objects.filter(contractor_id=contractor_id)
            except (ValueError, TypeError):
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('resource_type')
        
        # Проверка выполняется только если тип ресурса указан
        if not resource_type:
            return cleaned_data
            
        create_new_employee = cleaned_data.get('create_new_employee')
        create_new_contractor = cleaned_data.get('create_new_contractor')
        create_new_subcontractor = cleaned_data.get('create_new_subcontractor')
        create_new_equipment = cleaned_data.get('create_new_equipment')
        
        # Проверка, что выбран или создается ресурс в зависимости от типа
        # Но только если не создается новый ресурс
        if resource_type == 'employee':
            if not create_new_employee and not cleaned_data.get('employee'):
                # Не выбрасываем ошибку, если создается новый - это обработается в представлении
                if not self.data.get('employee-last_name'):  # Проверяем, что не создается новый
                    raise forms.ValidationError({
                        'employee': 'Необходимо выбрать сотрудника или создать нового'
                    })
        elif resource_type == 'contractor':
            if not create_new_contractor and not cleaned_data.get('contractor'):
                if not self.data.get('contractor-last_name'):  # Проверяем, что не создается новый
                    raise forms.ValidationError({
                        'contractor': 'Необходимо выбрать исполнителя или создать нового'
                    })
        elif resource_type == 'subcontractor':
            if not create_new_subcontractor and not cleaned_data.get('subcontractor'):
                if not self.data.get('subcontractor-name'):  # Проверяем, что не создается новый
                    raise forms.ValidationError({
                        'subcontractor': 'Необходимо выбрать субподрядчика или создать нового'
                    })
        elif resource_type == 'equipment':
            if not create_new_equipment and not cleaned_data.get('equipment'):
                if not self.data.get('equipment-name'):  # Проверяем, что не создается новый
                    raise forms.ValidationError({
                        'equipment': 'Необходимо выбрать оборудование или создать новое'
                    })
        
        return cleaned_data