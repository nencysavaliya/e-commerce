from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from .models import Product, Category, SubCategory


def product_list(request):
    """List all products with optional filtering"""
    products = Product.objects.filter(is_active=True).select_related('category', 'subcategory', 'seller')
    categories = Category.objects.filter(is_active=True)
    
    # Debug logging
    print(f"DEBUG: Initial products count: {products.count()}")
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
        print(f"DEBUG: After search filter '{query}', products count: {products.count()}")
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        print(f"DEBUG: After category filter '{category_slug}', products count: {products.count()}")
    
    # SubCategory filter
    subcategory_slug = request.GET.get('subcategory')
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
        print(f"DEBUG: After subcategory filter '{subcategory_slug}', products count: {products.count()}")
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    print(f"DEBUG: Final products in page: {len(products)}")
    print(f"DEBUG: Products object list: {products.object_list}")
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'current_category': category_slug,
        'current_sort': sort_by,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """Display product details"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory', 'seller'),
        slug=slug,
        is_active=True
    )
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get product reviews
    reviews = product.reviews.select_related('user').order_by('-created_at')
    
    # Get product attributes
    attribute_mappings = product.attribute_mappings.select_related('attribute_value__attribute')
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'attribute_mappings': attribute_mappings,
    }
    return render(request, 'products/product_detail.html', context)


def category_products(request, category_slug):
    """List products by category"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    subcategories = category.subcategories.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
    }
    return render(request, 'products/category_products.html', context)


def subcategory_products(request, category_slug, subcategory_slug):
    """List products by subcategory"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=category, is_active=True)
    products = Product.objects.filter(subcategory=subcategory, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'category': category,
        'subcategory': subcategory,
        'products': products,
    }
    return render(request, 'products/subcategory_products.html', context)


def search_products(request):
    """Search products"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'products/search_results.html', context)
