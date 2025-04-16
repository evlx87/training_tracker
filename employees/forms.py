from django import forms
from .models import Employee, TrainingProgram, TrainingRecord


class EmployeeForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    dismissal_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
                                     required=False)

    class Meta:
        model = Employee
        fields = [
            'last_name',
            'first_name',
            'middle_name',
            'birth_date',
            'position',
            'department',
            'is_dismissed',
            'dismissal_date',
            'is_on_maternity_leave',
            'is_external_part_time',
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-input'}),
            'position': forms.Select(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'is_dismissed': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_on_maternity_leave': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_external_part_time': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_dismissed = cleaned_data.get('is_dismissed')
        dismissal_date = cleaned_data.get('dismissal_date')
        if is_dismissed and not dismissal_date:
            raise forms.ValidationError("Укажите дату увольнения, если сотрудник уволен.")
        if not is_dismissed and dismissal_date:
            raise forms.ValidationError("Дата увольнения указывается только для уволенных сотрудников.")
        return cleaned_data


class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = ['name', 'recurrence_period']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'recurrence_period': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
        }


class TrainingRecordForm(forms.ModelForm):
    completion_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        label="Дата прохождения"
    )

    class Meta:
        model = TrainingRecord
        fields = ['training_program', 'completion_date']
        widgets = {
            'training_program': forms.Select(attrs={'class': 'form-input'}),
        }