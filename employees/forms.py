from django import forms
from django.core.exceptions import ValidationError
from .models import Employee, Department, Position, TrainingProgram, TrainingRecord

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'last_name', 'first_name', 'middle_name', 'birth_date', 'position',
            'department', 'hire_date', 'is_dismissed', 'dismissal_date',
            'is_on_maternity_leave', 'is_external_part_time'
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-input'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'position': forms.Select(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'is_dismissed': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'dismissal_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'is_on_maternity_leave': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_external_part_time': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_dismissed = cleaned_data.get('is_dismissed')
        dismissal_date = cleaned_data.get('dismissal_date')
        if is_dismissed and not dismissal_date:
            raise ValidationError('Укажите дату увольнения, если сотрудник уволен.')
        if not is_dismissed and dismissal_date:
            raise ValidationError('Дата увольнения должна быть пустой, если сотрудник не уволен.')
        return cleaned_data

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea'}),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
        }

class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = ['name', 'recurrence_period']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'recurrence_period': forms.NumberInput(attrs={'class': 'form-input'}),
        }

class TrainingRecordForm(forms.ModelForm):
    class Meta:
        model = TrainingRecord
        fields = ['training_program', 'completion_date']
        widgets = {
            'training_program': forms.Select(attrs={'class': 'form-input'}),
            'completion_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
