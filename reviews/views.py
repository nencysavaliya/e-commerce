from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from orders.models import OrderItem
from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, product_id):
    """Add a review for a product"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__payment_status='paid'
    ).exists()
    
    # Check if user already reviewed this product
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    
    if request.method == 'POST':
        if existing_review:
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Review submitted successfully'})
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('products:product_detail', slug=product.slug)
    else:
        if existing_review:
            form = ReviewForm(instance=existing_review)
        else:
            form = ReviewForm()
    
    context = {
        'form': form,
        'product': product,
        'has_purchased': has_purchased,
        'existing_review': existing_review,
    }
    return render(request, 'reviews/add_review.html', context)


@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    
    messages.success(request, 'Review deleted successfully.')
    return redirect('products:product_detail', slug=product_slug)


def product_reviews(request, product_id):
    """Get all reviews for a product"""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product, is_approved=True).select_related('user')
    
    return render(request, 'reviews/product_reviews.html', {
        'product': product,
        'reviews': reviews
    })
