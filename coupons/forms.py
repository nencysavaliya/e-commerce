from django import forms
from .models import Coupon
from django.utils import timezone


class CouponForm(forms.ModelForm):
    """Form for creating and editing coupons"""
    
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'discount_value', 'min_order_amount', 
                  'max_discount', 'usage_limit', 'expiry_date', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter coupon code (e.g., SAVE20)',
                'style': 'text-transform: uppercase;'
            }),
            'discount_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'discount_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discount value',
                'step': '0.01',
                'min': '0'
            }),
            'min_order_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum order amount',
                'step': '0.01',
                'min': '0',
                'value': '0'
            }),
            'max_discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum discount (optional)',
                'step': '0.01',
                'min': '0'
            }),
            'usage_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usage limit (0 for unlimited)',
                'min': '0',
                'value': '0'
            }),
            'expiry_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'code': 'Coupon Code',
            'discount_type': 'Discount Type',
            'discount_value': 'Discount Value',
            'min_order_amount': 'Minimum Order Amount (₹)',
            'max_discount': 'Maximum Discount Amount (₹)',
            'usage_limit': 'Usage Limit',
            'expiry_date': 'Expiry Date & Time',
            'is_active': 'Active'
        }
        help_texts = {
            'code': 'Unique code that customers will use',
            'discount_value': 'Percentage or flat amount based on discount type',
            'max_discount': 'Maximum discount for percentage type (leave empty for no limit)',
            'usage_limit': 'Total number of times this coupon can be used (0 for unlimited)',
            'expiry_date': 'Date and time when this coupon will expire'
        }
    
    def clean_code(self):
        """Convert code to uppercase"""
        code = self.cleaned_data.get('code', '')
        return code.strip().upper()
    
    def clean_expiry_date(self):
        """Validate expiry date is in the future"""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date < timezone.now():
            raise forms.ValidationError('Expiry date must be in the future.')
        return expiry_date
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        discount_type = cleaned_data.get('discount_type')
        discount_value = cleaned_data.get('discount_value')
        
        if discount_type == 'percentage' and discount_value:
            if discount_value > 100:
                raise forms.ValidationError({
                    'discount_value': 'Percentage discount cannot be more than 100%'
                })
            if discount_value <= 0:
                raise forms.ValidationError({
                    'discount_value': 'Discount value must be greater than 0'
                })
        
        return cleaned_data
