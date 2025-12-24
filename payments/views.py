from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .models import Payment
import json


@login_required
def initiate_payment(request, order_id):
    """Initiate payment for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        messages.info(request, 'This order is already paid.')
        return redirect('orders:order_detail', order_id=order.id)
    
    # Create or get payment record
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={'amount': order.final_amount}
    )
    
    # Check if Razorpay is configured
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        try:
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(order.final_amount * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': 1
            })
            
            payment.razorpay_order_id = razorpay_order['id']
            payment.save()
            
            context = {
                'order': order,
                'payment': payment,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': int(order.final_amount * 100),
            }
            return render(request, 'payments/payment.html', context)
        except Exception as e:
            messages.error(request, 'Payment gateway error. Please try again.')
    
    # Fallback to COD
    context = {
        'order': order,
        'payment': payment,
        'cod_only': True,
    }
    return render(request, 'payments/payment.html', context)


@csrf_exempt
def payment_callback(request):
    """Handle Razorpay payment callback"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
            
            payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
            
            # Verify signature
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                client.utility.verify_payment_signature(params_dict)
                
                # Update payment
                payment.payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.payment_status = 'completed'
                payment.save()
                
                # Update order
                payment.order.payment_status = 'paid'
                payment.order.order_status = 'confirmed'
                payment.order.save()
                
                return JsonResponse({'success': True, 'order_id': payment.order.id})
            except razorpay.errors.SignatureVerificationError:
                payment.payment_status = 'failed'
                payment.save()
                return JsonResponse({'success': False, 'error': 'Invalid signature'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def cod_payment(request, order_id):
    """Process Cash on Delivery payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.final_amount,
            'payment_method': 'cod',
            'payment_status': 'pending'
        }
    )
    
    if not created:
        payment.payment_method = 'cod'
        payment.save()
    
    order.order_status = 'confirmed'
    order.save()
    
    messages.success(request, 'Order placed successfully! Pay on delivery.')
    return redirect('orders:order_confirmation', order_id=order.id)


@login_required
def payment_success(request, order_id):
    """Payment success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/success.html', {'order': order})


@login_required
def payment_failed(request, order_id):
    """Payment failed page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/failed.html', {'order': order})
