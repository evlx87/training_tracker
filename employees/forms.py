from datetime import date

from django import forms

from .models import Employee, TrainingRecord


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'last_name',
            'first_name',
            'middle_name',
            'birth_date',
            'hire_date',
            'dismissal_date',
            'position',
            'department']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'dismissal_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        if birth_date and birth_date > date.today():
            raise forms.ValidationError(
                'Дата рождения не может быть в будущем.')
        return birth_date


class TrainingRecordForm(forms.ModelForm):
    class Meta:
        model = TrainingRecord
        fields = [
            'employee',
            'training_program',
            'completion_date',
            'expiry_date']
        widgets = {
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
