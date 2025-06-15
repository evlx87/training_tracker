from django import forms
from .models import Position


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'is_manager', 'is_teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'is_manager': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_teacher': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
