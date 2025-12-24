from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Coupon, CouponUsage


@login_required
def apply_coupon(request):
    """Apply coupon to cart/order"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        order_amount = float(request.POST.get('order_amount', 0))
        
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
    coupons = Coupon.objects.filter(is_active=True, expiry_date__gt=timezone.now())
    return render(request, 'coupons/available_coupons.html', {'coupons': coupons})
