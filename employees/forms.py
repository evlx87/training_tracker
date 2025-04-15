from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    birth_date = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=forms.DateInput(attrs={'placeholder': 'ДД.ММ.ГГГГ'}),
        label="Дата рождения"
    )
    dismissal_date = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=forms.DateInput(attrs={'placeholder': 'ДД.ММ.ГГГГ'}),
        required=False,
        label="Дата увольнения"
    )

    class Meta:
        model = Employee
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        is_dismissed = cleaned_data.get('is_dismissed')
        dismissal_date = cleaned_data.get('dismissal_date')

        # Проверка: если сотрудник уволен, дата увольнения обязательна
        if is_dismissed and not dismissal_date:
            raise forms.ValidationError("Укажите дату увольнения для уволенного сотрудника.")
        # Проверка: если сотрудник не уволен, дата увольнения не нужна
        if not is_dismissed and dismissal_date:
            raise forms.ValidationError("Дата увольнения не должна указываться для неуволенного сотрудника.")

        return cleaned_data