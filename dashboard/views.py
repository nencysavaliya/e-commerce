from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from products.models import Product, Category
from orders.models import Order


def seller_required(view_func):
    """Decorator to check if user is a seller"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_seller or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Seller account required.')
        return redirect('home')
    return wrapper


@login_required
@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with full access"""
    # Get statistics
    total_users = User.objects.count()
    total_sellers = User.objects.filter(is_seller=True).count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    
    # Revenue
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('final_amount'))['total'] or 0
    
    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Orders by status
    pending_orders = Order.objects.filter(order_status='pending').count()
    confirmed_orders = Order.objects.filter(order_status='confirmed').count()
    shipped_orders = Order.objects.filter(order_status='shipped').count()
    delivered_orders = Order.objects.filter(order_status='delivered').count()
    
    # Monthly revenue (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_revenue = Order.objects.filter(
        payment_status='paid',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('final_amount'))['total'] or 0
    
    context = {
        'total_users': total_users,
        'total_sellers': total_sellers,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
    }
    return render(request, 'dashboard/admin/dashboard.html', context)


@login_required
@seller_required
def seller_dashboard(request):
    """Seller dashboard with limited access"""
    # Get seller's products
    seller_products = Product.objects.filter(seller=request.user)
    total_products = seller_products.count()
    active_products = seller_products.filter(is_active=True).count()
    
    # Get seller's orders (orders containing their products)
    from orders.models import OrderItem
    seller_order_items = OrderItem.objects.filter(
        product__seller=request.user
    ).select_related('order')
    
    seller_orders = Order.objects.filter(
        items__product__seller=request.user
    ).distinct()
    
    total_orders = seller_orders.count()
    
    # Revenue from seller's products
    total_revenue = seller_order_items.filter(
        order__payment_status='paid'
    ).aggregate(total=Sum('price'))['total'] or 0
    
    # Recent orders
    recent_orders = seller_orders.order_by('-created_at')[:10]
    
    # Low stock products
    low_stock_products = seller_products.filter(stock__lte=5, is_active=True)
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'dashboard/seller/dashboard.html', context)


# Admin Management Views
@login_required
@staff_member_required
def admin_users(request):
    """Manage users"""
    users = User.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin/users.html', {'users': users})


@login_required
@staff_member_required
def admin_toggle_user(request, user_id):
    """Block/unblock user"""
    user = get_object_or_404(User, id=user_id)
    if not user.is_superuser:
        user.is_active = not user.is_active
        user.save()
        action = 'unblocked' if user.is_active else 'blocked'
        messages.success(request, f'User {user.username} has been {action}.')
    return redirect('dashboard:admin_users')


@login_required
@staff_member_required
def admin_make_seller(request, user_id):
    """Make user a seller"""
    user = get_object_or_404(User, id=user_id)
    user.is_seller = not user.is_seller
    user.save()
    action = 'is now a seller' if user.is_seller else 'is no longer a seller'
    messages.success(request, f'User {user.username} {action}.')
    return redirect('dashboard:admin_users')


@login_required
@staff_member_required
def admin_view_user(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    # Get user's orders
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    # Get user's products if seller
    products = None
    if user.is_seller:
        products = Product.objects.filter(seller=user)[:10]
    
    context = {
        'viewed_user': user,
        'orders': orders,
        'products': products,
    }
    return render(request, 'dashboard/admin/user_detail.html', context)


@login_required
@staff_member_required
def admin_edit_user(request, user_id):
    """Edit user details"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.is_seller = request.POST.get('is_seller') == '1'
        user.is_active = request.POST.get('is_active') == '1'
        
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, f'User {user.username} updated successfully!')
        return redirect('dashboard:admin_users')
    
    return render(request, 'dashboard/admin/user_edit.html', {'edited_user': user})


@login_required
@staff_member_required
def admin_products(request):
    """Manage all products"""
    products = Product.objects.select_related('category', 'seller').all()
    categories = Category.objects.all()
    return render(request, 'dashboard/admin/products.html', {
        'products': products,
        'categories': categories
    })


@login_required
@staff_member_required
def admin_add_product(request):
    """Add new product"""
    from products.models import SubCategory
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price') or None
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory') or None
        image = request.FILES.get('image')
        is_active = request.POST.get('is_active') == '1'
        
        if name and price and category_id:
            from django.utils.text import slugify
            slug = slugify(name)
            counter = 1
            original_slug = slug
            while Product.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            product = Product.objects.create(
                seller=request.user,
                name=name,
                slug=slug,
                description=description,
                price=price,
                discount_price=discount_price,
                stock=stock,
                category_id=category_id,
                subcategory_id=subcategory_id,
                image=image,
                is_active=is_active
            )
            messages.success(request, f'Product "{name}" created successfully!')
            return redirect('dashboard:admin_products')
        else:
            messages.error(request, 'Name, price, and category are required.')
    
    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    return render(request, 'dashboard/admin/product_form.html', {
        'action': 'Add',
        'categories': categories
    })


@login_required
@staff_member_required
def admin_edit_product(request, product_id):
    """Edit product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description', product.description)
        product.price = request.POST.get('price', product.price)
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock', product.stock)
        product.category_id = request.POST.get('category', product.category_id)
        product.subcategory_id = request.POST.get('subcategory') or None
        product.is_active = request.POST.get('is_active') == '1'
        
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        
        # Update slug if name changed
        from django.utils.text import slugify
        new_slug = slugify(product.name)
        if new_slug != product.slug:
            counter = 1
            original_slug = new_slug
            while Product.objects.filter(slug=new_slug).exclude(id=product.id).exists():
                new_slug = f"{original_slug}-{counter}"
                counter += 1
            product.slug = new_slug
        
        product.save()
        messages.success(request, f'Product "{product.name}" updated successfully!')
        return redirect('dashboard:admin_products')
    
    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    return render(request, 'dashboard/admin/product_form.html', {
        'action': 'Edit',
        'product': product,
        'categories': categories
    })


@login_required
@staff_member_required
def admin_delete_product(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.success(request, f'Product "{name}" deleted successfully!')
    return redirect('dashboard:admin_products')


@login_required
@staff_member_required
def admin_view_product(request, product_id):
    """View product details"""
    product = get_object_or_404(Product.objects.select_related('category', 'subcategory', 'seller'), id=product_id)
    reviews = product.reviews.select_related('user').order_by('-created_at')[:10]
    
    return render(request, 'dashboard/admin/product_detail.html', {
        'product': product,
        'reviews': reviews
    })


@login_required
@staff_member_required
def admin_orders(request):
    """Manage all orders"""
    orders = Order.objects.select_related('user', 'address').prefetch_related('items').all()
    return render(request, 'dashboard/admin/orders.html', {'orders': orders})


@login_required
@staff_member_required
def admin_update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.order_status = new_status
            order.save()
            messages.success(request, f'Order {order.order_number} status updated to {new_status}.')
    return redirect('dashboard:admin_orders')


@login_required
@staff_member_required  
def admin_categories(request):
    """Manage categories"""
    categories = Category.objects.prefetch_related('subcategories').all()
    return render(request, 'dashboard/admin/categories.html', {'categories': categories})


@login_required
@staff_member_required
def admin_add_category(request):
    """Add new category"""
    from products.models import SubCategory
    
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        is_active = request.POST.get('is_active') == '1'
        
        if name:
            from django.utils.text import slugify
            slug = slugify(name)
            # Make slug unique
            counter = 1
            original_slug = slug
            while Category.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            category = Category.objects.create(
                name=name,
                slug=slug,
                image=image,
                is_active=is_active
            )
            messages.success(request, f'Category "{name}" created successfully!')
            return redirect('dashboard:admin_categories')
        else:
            messages.error(request, 'Category name is required.')
    
    return render(request, 'dashboard/admin/category_form.html', {'action': 'Add'})


@login_required
@staff_member_required
def admin_edit_category(request, category_id):
    """Edit category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name', category.name)
        category.is_active = request.POST.get('is_active') == '1'
        
        if request.FILES.get('image'):
            category.image = request.FILES['image']
        
        # Update slug if name changed
        from django.utils.text import slugify
        new_slug = slugify(category.name)
        if new_slug != category.slug:
            counter = 1
            original_slug = new_slug
            while Category.objects.filter(slug=new_slug).exclude(id=category.id).exists():
                new_slug = f"{original_slug}-{counter}"
                counter += 1
            category.slug = new_slug
        
        category.save()
        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('dashboard:admin_categories')
    
    return render(request, 'dashboard/admin/category_form.html', {
        'action': 'Edit',
        'category': category
    })


@login_required
@staff_member_required
def admin_delete_category(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)
    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" deleted successfully!')
    return redirect('dashboard:admin_categories')


@login_required
@staff_member_required
def admin_add_subcategory(request):
    """Add subcategory"""
    from products.models import SubCategory
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        is_active = request.POST.get('is_active') == '1'
        
        if name and category_id:
            from django.utils.text import slugify
            slug = slugify(name)
            counter = 1
            original_slug = slug
            while SubCategory.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            SubCategory.objects.create(
                name=name,
                slug=slug,
                category_id=category_id,
                is_active=is_active
            )
            messages.success(request, f'Subcategory "{name}" created successfully!')
        else:
            messages.error(request, 'Name and category are required.')
    
    return redirect('dashboard:admin_categories')


@login_required
@staff_member_required
def admin_coupons(request):
    """Manage coupons"""
    from coupons.models import Coupon
    coupons = Coupon.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin/coupons.html', {'coupons': coupons})


@login_required
@staff_member_required
def admin_add_coupon(request):
    """Add new coupon"""
    from coupons.models import Coupon
    from coupons.forms import CouponForm
    
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, f'Coupon "{coupon.code}" created successfully!')
            return redirect('dashboard:admin_coupons')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CouponForm()
    
    return render(request, 'dashboard/admin/coupon_form.html', {
        'form': form,
        'action': 'Add',
        'title': 'Add New Coupon'
    })


@login_required
@staff_member_required
def admin_edit_coupon(request, coupon_id):
    """Edit existing coupon"""
    from coupons.models import Coupon
    from coupons.forms import CouponForm
    
    coupon = get_object_or_404(Coupon, id=coupon_id)
    
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, f'Coupon "{coupon.code}" updated successfully!')
            return redirect('dashboard:admin_coupons')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CouponForm(instance=coupon)
    
    return render(request, 'dashboard/admin/coupon_form.html', {
        'form': form,
        'coupon': coupon,
        'action': 'Edit',
        'title': f'Edit Coupon: {coupon.code}'
    })


@login_required
@staff_member_required
def admin_delete_coupon(request, coupon_id):
    """Delete coupon"""
    from coupons.models import Coupon
    
    coupon = get_object_or_404(Coupon, id=coupon_id)
    code = coupon.code
    coupon.delete()
    messages.success(request, f'Coupon "{code}" deleted successfully!')
    return redirect('dashboard:admin_coupons')



@login_required
@staff_member_required
def admin_reviews(request):
    """Manage reviews"""
    from reviews.models import Review
    reviews = Review.objects.select_related('user', 'product').all()
    return render(request, 'dashboard/admin/reviews.html', {'reviews': reviews})


# Seller Management Views
@login_required
@seller_required
def seller_products(request):
    """Seller's products"""
    products = Product.objects.filter(seller=request.user)
    return render(request, 'dashboard/seller/products.html', {'products': products})


@login_required
@seller_required
def seller_orders(request):
    """Seller's orders"""
    from orders.models import OrderItem
    order_items = OrderItem.objects.filter(
        product__seller=request.user
    ).select_related('order', 'product').order_by('-order__created_at')
    return render(request, 'dashboard/seller/orders.html', {'order_items': order_items})


@login_required
@seller_required
def seller_add_product(request):
    """Add new product"""
    from products.models import Category, SubCategory
    from django.core.files.storage import default_storage
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price') or None
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory') or None
        image = request.FILES.get('image')
        
        if name and price and category_id and image:
            product = Product.objects.create(
                seller=request.user,
                name=name,
                description=description,
                price=price,
                discount_price=discount_price,
                stock=stock,
                category_id=category_id,
                subcategory_id=subcategory_id,
                image=image,
                is_active=True
            )
            messages.success(request, 'Product added successfully!')
            return redirect('dashboard:seller_products')
        else:
            messages.error(request, 'Please fill all required fields.')
    
    categories = Category.objects.filter(is_active=True)
    return render(request, 'dashboard/seller/add_product.html', {'categories': categories})


@login_required
@seller_required
def seller_edit_product(request, product_id):
    """Edit product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description', product.description)
        product.price = request.POST.get('price', product.price)
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock', product.stock)
        product.category_id = request.POST.get('category', product.category_id)
        product.subcategory_id = request.POST.get('subcategory') or None
        product.is_active = request.POST.get('is_active') == 'on'
        
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('dashboard:seller_products')
    
    categories = Category.objects.filter(is_active=True)
    return render(request, 'dashboard/seller/edit_product.html', {
        'product': product,
        'categories': categories
    })


@login_required
@seller_required
def seller_delete_product(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('dashboard:seller_products')
