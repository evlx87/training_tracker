from django import forms
from .models import TrainingProgram

class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = ['name', 'duration_days']