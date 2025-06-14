from django import forms
from .models import TrainingProgram

class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = ['name', 'recurrence_period']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-input'}),
            'recurrence_period': forms.NumberInput(
                attrs={
                    'class': 'form-input'}),
        }