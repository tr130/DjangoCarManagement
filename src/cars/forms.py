from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('title', 'description', 'car', 'employee', 'expected_complete', 'estimated_time', 'manager')
        widgets = {
            'expected_complete': forms.DateInput(attrs={'type': 'date'}),
        }