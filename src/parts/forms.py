from django import forms
from .models import Part

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ('name', 'cost_price', 'customer_price', 'stock_level')