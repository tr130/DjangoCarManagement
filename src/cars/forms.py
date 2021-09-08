from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Job, LabourUnit, Message, PartRequest, PartUnit

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

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('sender', 'recipient', 'car', 'job', 'subject', 'body')
        widgets = {
            'sender': forms.HiddenInput(),
            'recipient': forms.HiddenInput(),
            'car': forms.HiddenInput(),
            'job': forms.HiddenInput(),
            'body': forms.Textarea(attrs={'rows':'5'})
        }

class PartRequestForm(forms.ModelForm):
    class Meta:
        model = PartRequest
        fields = ('part', 'notes', 'quantity', 'requested_by', 'assigned_to', 'job',)
        labels = {
            'notes': _('Further Information (if the part is not listed, state what you need here):')
        }
        widgets = {
            'requested_by': forms.HiddenInput(),
            'job': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'rows': '5'})
        }