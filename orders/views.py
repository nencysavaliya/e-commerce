from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from cart.models import Cart
from .models import Address, Order, OrderItem
from .forms import AddressForm
from coupons.models import Coupon, CouponUsage


@login_required
def checkout(request):
    """Checkout page"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart')
    
    addresses = Address.objects.filter(user=request.user)
    
    # Get applied coupon from session
    applied_coupon = request.session.get('applied_coupon')
    discount_amount = 0
    final_amount = float(cart.subtotal)  # Convert to float for consistency
    
    if applied_coupon:
        try:
            coupon = Coupon.objects.get(id=applied_coupon['coupon_id'])
            # Re-validate coupon
            is_valid, message = coupon.is_valid(user=request.user, order_amount=float(cart.subtotal))
            if is_valid:
                discount_amount = float(coupon.calculate_discount(float(cart.subtotal)))
                final_amount = float(cart.subtotal) - discount_amount
                # Update session with fresh discount
                applied_coupon['discount'] = discount_amount
            else:
                # Coupon is no longer valid, remove it
                del request.session['applied_coupon']
                applied_coupon = None
                messages.warning(request, f'Coupon removed: {message}')
        except Coupon.DoesNotExist:
            del request.session['applied_coupon']
            applied_coupon = None
    
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        
        if not address_id:
            messages.error(request, 'Please select a delivery address.')
            return redirect('orders:checkout')
        
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Create order with coupon discount if applied
        total_amount = cart.subtotal
        order_discount = 0
        order_final_amount = total_amount
        used_coupon = None
        
        # Re-check coupon at order creation
        if applied_coupon:
            try:
                used_coupon = Coupon.objects.get(id=applied_coupon['coupon_id'])
                is_valid, message = used_coupon.is_valid(user=request.user, order_amount=float(total_amount))
                if is_valid:
                    order_discount = float(used_coupon.calculate_discount(float(total_amount)))
                    order_final_amount = float(total_amount) - order_discount
                else:
                    messages.warning(request, f'Coupon could not be applied: {message}')
                    used_coupon = None
            except Coupon.DoesNotExist:
                used_coupon = None
        
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total_amount,
            discount_amount=order_discount,
            final_amount=order_final_amount
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.product.display_price
            )
            
            # Reduce stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Create coupon usage record if coupon was used
        if used_coupon:
            CouponUsage.objects.create(
                coupon=used_coupon,
                user=request.user
            )
            # Clear coupon from session
            if 'applied_coupon' in request.session:
                del request.session['applied_coupon']
        
        # Clear cart
        cart.clear()
        
        return redirect('payments:initiate', order_id=order.id)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'address_form': AddressForm(),
        'applied_coupon': applied_coupon,
        'discount_amount': discount_amount,
        'final_amount': final_amount,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def add_address(request):
    """Add new shipping address"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # Set as default if it's the first address
            if not Address.objects.filter(user=request.user).exists():
                address.is_default = True
            
            address.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'address_id': address.id,
                    'address_text': str(address)
                })
            
            messages.success(request, 'Address added successfully.')
            return redirect('orders:checkout')
    else:
        form = AddressForm()
    
    return render(request, 'orders/add_address.html', {'form': form})


@login_required
def order_history(request):
    """View order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def cancel_order(request, order_id):
    """Cancel an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.order_status in ['pending', 'confirmed']:
        order.order_status = 'cancelled'
        order.save()
        
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        
        messages.success(request, f'Order {order.order_number} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('orders:order_detail', order_id=order.id)
