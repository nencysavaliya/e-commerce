import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from coupons.models import Coupon
from django.utils import timezone

print("Testing Coupon Validation Fix\n" + "="*50)

# Get SAVE20 coupon
try:
    coupon = Coupon.objects.get(code='SAVE20')
    
    print(f"\nCoupon: {coupon.code}")
    print(f"Discount: {coupon.discount_value}% OFF")
    print(f"Min Order: ₹{coupon.min_order_amount}")
    print(f"Expiry Date (DB): {coupon.expiry_date}")
    print(f"Is Active: {coupon.is_active}")
    
    print(f"\nCurrent DateTime: {timezone.now()}")
    print(f"Current Date: {timezone.now().date()}")
    
    # Test validation
    is_valid, message = coupon.is_valid(order_amount=1000)
    
    print(f"\n{'✅' if is_valid else '❌'} Validation Result: {message}")
    
    if is_valid:
        discount = coupon.calculate_discount(1000)
        print(f"💰 Discount on ₹1000: ₹{discount}")
        
except Coupon.DoesNotExist:
    print("❌ SAVE20 coupon not found!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
