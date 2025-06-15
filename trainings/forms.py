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

    def clean_name(self):
        name = self.cleaned_data['name']
        if TrainingProgram.objects.filter(
                name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Программа обучения с таким названием уже существует.")
        return name
