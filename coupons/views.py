from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Coupon, CouponUsage


@login_required
def apply_coupon(request):
    """Apply coupon to cart/order"""
    from decimal import Decimal
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        order_amount = Decimal(request.POST.get('order_amount', 0))
        
        try:
            coupon = Coupon.objects.get(code=code)
            is_valid, message = coupon.is_valid(user=request.user, order_amount=order_amount)
            
            if is_valid:
                discount = coupon.calculate_discount(order_amount)
                
                # Store coupon in session
                request.session['applied_coupon'] = {
                    'code': coupon.code,
                    'discount': float(discount),
                    'coupon_id': coupon.id
                }
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'discount': float(discount),
                        'message': f'Coupon applied! You save ₹{discount}'
                    })
                
                messages.success(request, f'Coupon applied! You save ₹{discount}')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': message})
                messages.error(request, message)
        except Coupon.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
            messages.error(request, 'Invalid coupon code')
    
    return redirect('orders:checkout')


@login_required
def remove_coupon(request):
    """Remove applied coupon"""
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Coupon removed'})
    
    messages.info(request, 'Coupon removed')
    return redirect('orders:checkout')


def available_coupons(request):
    """List available coupons"""
    from django.utils import timezone
    
    # Get all active coupons and filter in Python to avoid timezone issues
    all_coupons = Coupon.objects.filter(is_active=True)
    current_date = timezone.now().date()
    
    # Filter coupons by checking each one with date comparison
    valid_coupons = []
    for coupon in all_coupons:
        if timezone.is_aware(coupon.expiry_date):
            expiry_date = timezone.localtime(coupon.expiry_date).date()
        else:
            expiry_date = coupon.expiry_date.date()
        
        if expiry_date >= current_date:
            valid_coupons.append(coupon)
    
    return render(request, 'coupons/available_coupons.html', {'coupons': valid_coupons})
