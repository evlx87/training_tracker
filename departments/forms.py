from django import forms
from .models import Department


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if Department.objects.filter(name=name).exclude(
                pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Подразделение с таким названием уже существует.")
        return name
