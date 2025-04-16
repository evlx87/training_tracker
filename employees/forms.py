from django import forms
from .models import Employee, Department, Position, TrainingProgram, TrainingRecord

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['last_name', 'first_name', 'middle_name', 'position', 'department', 'hire_date']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-input'}),
            'position': forms.Select(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

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
        fields = ['name', 'description', 'recurrence_period']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea'}),
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