from django import forms
from .models import Address


class AddressForm(forms.ModelForm):
    """Form for adding/editing shipping address"""
    class Meta:
        model = Address
        fields = ['name', 'phone', 'address', 'city', 'state', 'pincode', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Street Address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN Code'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
