def cart_count(request):
    """Context processor to add cart count to all templates"""
    count = 0
    if request.user.is_authenticated:
        from .models import Cart
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items
        except Cart.DoesNotExist:
            pass
    return {'cart_count': count}
