from django import forms
from django.contrib.auth import get_user_model

from .models import CostCalculation, OrganizationSettings, RoleAssignment

User = get_user_model()

# Импортируем модели и формы из других приложений
try:
    from nmacost.models import NMACost
    from nmacost.forms import NMACostForm, ResourceItemForm
    from commercial_proposal.models import CommercialProposal
    from commercial_proposal.forms import CommercialProposalForm, ServiceItemFormSet
    HAS_NMA = True
    HAS_COMMERCIAL = True
except ImportError:
    HAS_NMA = False
    HAS_COMMERCIAL = False
    NMACost = None
    CommercialProposal = None


class StyledFormMixin:
    """Добавляет классы Bootstrap всем полям формы."""

    def _apply_styling(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if "form-control" not in css_class and "form-select" not in css_class and not isinstance(
                field.widget, forms.CheckboxInput
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class CostCalculationForm(StyledFormMixin, forms.ModelForm):
    # Поля для выбора источника данных
    nma_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующую форму НМА'),
            ('new', 'Создать новую форму НМА'),
        ],
        label="Источник данных НМА",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_nma = forms.ModelChoiceField(
        queryset=NMACost.objects.all().order_by('-created_at') if (HAS_NMA and NMACost) else forms.ModelChoiceField.empty_queryset,
        label="Выбрать форму НМА",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    commercial_source = forms.ChoiceField(
        choices=[
            ('none', 'Не использовать'),
            ('existing', 'Выбрать существующее коммерческое предложение'),
            ('new', 'Создать новое коммерческое предложение'),
        ],
        label="Источник данных коммерческого предложения",
        initial='none',
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=False,
    )
    existing_commercial = forms.ModelChoiceField(
        queryset=CommercialProposal.objects.all().order_by('-creation_date') if (HAS_COMMERCIAL and CommercialProposal) else forms.ModelChoiceField.empty_queryset,
        label="Выбрать коммерческое предложение",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = CostCalculation
        fields = [
            "project_name",
            "client_name",
            "project_brief",
            "estimated_hours",
            "hourly_rate",
            "infrastructure_cost",
            "other_expenses",
            "management_overhead_percent",
            "risk_percent",
            "profit_margin_percent",
            "asset_capitalization_percent",
            "commercial_markup_percent",
            "nma_cost",
            "commercial_proposal",
        ]
        widgets = {
            "project_brief": forms.Textarea(attrs={"rows": 4}),
            "nma_cost": forms.Select(attrs={"class": "form-select"}),
            "commercial_proposal": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем прямые поля выбора, они будут использоваться через nma_source/commercial_source
        # Заменяем ModelChoiceField на CharField для скрытых полей, чтобы избежать проблем с валидацией пустых значений
        if 'nma_cost' in self.fields:
            # Сохраняем оригинальный label
            original_label = self.fields['nma_cost'].label
            # Заменяем на CharField для более гибкой обработки
            self.fields['nma_cost'] = forms.CharField(
                required=False,
                widget=forms.HiddenInput(),
                label=original_label
            )
        if 'commercial_proposal' in self.fields:
            # Сохраняем оригинальный label
            original_label = self.fields['commercial_proposal'].label
            # Заменяем на CharField для более гибкой обработки
            self.fields['commercial_proposal'] = forms.CharField(
                required=False,
                widget=forms.HiddenInput(),
                label=original_label
            )
        
        # Если приложения недоступны, скрываем соответствующие поля
        if not HAS_NMA:
            if 'nma_source' in self.fields:
                self.fields['nma_source'].widget = forms.HiddenInput()
            if 'existing_nma' in self.fields:
                self.fields['existing_nma'].widget = forms.HiddenInput()
        
        if not HAS_COMMERCIAL:
            if 'commercial_source' in self.fields:
                self.fields['commercial_source'].widget = forms.HiddenInput()
            if 'existing_commercial' in self.fields:
                self.fields['existing_commercial'].widget = forms.HiddenInput()
        
        # Если редактируем существующий расчет, устанавливаем значения
        if self.instance and self.instance.pk:
            if self.instance.nma_cost:
                self.fields['nma_source'].initial = 'existing'
                self.fields['existing_nma'].initial = self.instance.nma_cost
            if self.instance.commercial_proposal:
                self.fields['commercial_source'].initial = 'existing'
                self.fields['existing_commercial'].initial = self.instance.commercial_proposal
    
    def clean_nma_cost(self):
        """Преобразует строковое значение в объект NMACost или возвращает None."""
        # Получаем значение из cleaned_data (CharField всегда возвращает строку)
        nma_value = self.cleaned_data.get('nma_cost', '')
        # Если значение пустое или отсутствует, возвращаем None
        if not nma_value or nma_value == '':
            return None
        # Если значение есть, пытаемся получить объект по ID
        try:
            if HAS_NMA:
                from nmacost.models import NMACost
                return NMACost.objects.get(pk=nma_value)
        except (NMACost.DoesNotExist, ValueError, TypeError):
            pass
        return None
    
    def clean_commercial_proposal(self):
        """Преобразует строковое значение в объект CommercialProposal или возвращает None."""
        # Получаем значение из cleaned_data (CharField всегда возвращает строку)
        commercial_value = self.cleaned_data.get('commercial_proposal', '')
        # Если значение пустое или отсутствует, возвращаем None
        if not commercial_value or commercial_value == '':
            return None
        # Если значение есть, пытаемся получить объект по ID
        try:
            if HAS_COMMERCIAL:
                from commercial_proposal.models import CommercialProposal
                return CommercialProposal.objects.get(pk=commercial_value)
        except (CommercialProposal.DoesNotExist, ValueError, TypeError):
            pass
        return None


class OrganizationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "company_name",
            "director_full_name",
            "director_position",
            "logo",
            "contact_phone",
            "contact_email",
        ]


class RoleAssignmentForm(StyledFormMixin, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = RoleAssignment
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }

