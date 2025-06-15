from django import forms
from .models import Employee, DeletionRequest, TrainingRecord


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'last_name',
            'first_name',
            'middle_name',
            'birth_date',
            'position',
            'department',
            'hire_date',
            'is_dismissed',
            'dismissal_date',
            'is_on_maternity_leave',
            'is_external_part_time',
            'is_safety_commission_member',
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-input'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'text', 'placeholder': 'ДД.ММ.ГГГГ'}),
            'position': forms.Select(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'text', 'placeholder': 'ДД.ММ.ГГГГ'}),
            'dismissal_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'text', 'placeholder': 'ДД.ММ.ГГГГ'}),
            'is_dismissed': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_on_maternity_leave': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_external_part_time': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_safety_commission_member': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class TrainingRecordForm(forms.ModelForm):
    class Meta:
        model = TrainingRecord
        fields = ['training_program', 'completion_date']
        widgets = {
            'training_program': forms.Select(attrs={'class': 'form-input'}),
            'completion_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'text', 'placeholder': 'ДД.ММ.ГГГГ'}),
        }


class DeletionRequestForm(forms.ModelForm):
    class Meta:
        model = DeletionRequest
        fields = []
