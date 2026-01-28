def wishlist_count(request):
    """Context processor to add wishlist count to all templates"""
    count = 0
    if request.user.is_authenticated:
        from .models import Wishlist
        count = Wishlist.objects.filter(user=request.user).count()
    return {'wishlist_count': count}
