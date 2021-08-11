from django import forms
from .models import Job, LabourUnit, PartUnit

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('title', 'description', 'car', 'employee', 'expected_complete', 'estimated_time', 'manager')
        widgets = {
            'expected_complete': forms.DateInput(attrs={'type': 'date'}),
        }

class LabourUnitForm(forms.ModelForm):
    class Meta:
        model = LabourUnit
        fields = ('description', 'time_spent', 'employee', 'job')
        widgets = {
            'employee': forms.HiddenInput(),
            'job': forms.HiddenInput(),
        }

class PartUnitForm(forms.ModelForm):
    class Meta:
        model = PartUnit
        fields = ('part', 'quantity', 'added_by', 'job')
        widgets = {
            'added_by': forms.HiddenInput(),
            'job': forms.HiddenInput(),
        }