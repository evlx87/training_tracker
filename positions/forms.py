from django import forms
from .models import Position

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError('Название должности должно содержать минимум 3 символа.')
        return name