# staff/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['patronymic', 'position']
        labels = {
            'patronymic': 'Отчество',
            'position': 'Должность'
        }
        widgets = {
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'})
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта')
    last_name = forms.CharField(required=True, label='Фамилия')
    first_name = forms.CharField(required=True, label='Имя')

    # Поля профиля
    patronymic = forms.CharField(required=False, label='Отчество')
    position = forms.CharField(required=False, label='Должность')

    roles = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Роли',
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем классы Bootstrap к полям
        for field_name in self.fields:
            if field_name not in ['roles']:
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Сохраняем роли
            user.groups.set(self.cleaned_data['roles'])

            # Создаем или обновляем профиль
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.patronymic = self.cleaned_data['patronymic']
            profile.position = self.cleaned_data['position']
            profile.save()

        return user


class CustomUserChangeForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Электронная почта')
    last_name = forms.CharField(required=True, label='Фамилия')
    first_name = forms.CharField(required=True, label='Имя')

    # Поля профиля
    patronymic = forms.CharField(required=False, label='Отчество')
    position = forms.CharField(required=False, label='Должность')

    roles = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Роли',
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'email', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем классы Bootstrap к полям
        for field_name in self.fields:
            if field_name not in ['roles', 'is_active']:
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})

        # Устанавливаем начальные значения
        if self.instance.pk:
            # Роли
            self.fields['roles'].initial = self.instance.groups.all()

            # Данные профиля
            try:
                profile = self.instance.profile
                self.fields['patronymic'].initial = profile.patronymic
                self.fields['position'].initial = profile.position
            except UserProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            # Сохраняем роли
            user.groups.set(self.cleaned_data['roles'])

            # Сохраняем профиль
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.patronymic = self.cleaned_data['patronymic']
            profile.position = self.cleaned_data['position']
            profile.save()

        return user