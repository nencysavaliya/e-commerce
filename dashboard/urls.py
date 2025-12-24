from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Admin Dashboard
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin/users/<int:user_id>/make-seller/', views.admin_make_seller, name='admin_make_seller'),
    path('admin/users/<int:user_id>/view/', views.admin_view_user, name='admin_view_user'),
    path('admin/users/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/add/', views.admin_add_product, name='admin_add_product'),
    path('admin/products/<int:product_id>/edit/', views.admin_edit_product, name='admin_edit_product'),
    path('admin/products/<int:product_id>/delete/', views.admin_delete_product, name='admin_delete_product'),
    path('admin/products/<int:product_id>/view/', views.admin_view_product, name='admin_view_product'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/<int:order_id>/update-status/', views.admin_update_order_status, name='admin_update_order_status'),
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/add/', views.admin_add_category, name='admin_add_category'),
    path('admin/categories/<int:category_id>/edit/', views.admin_edit_category, name='admin_edit_category'),
    path('admin/categories/<int:category_id>/delete/', views.admin_delete_category, name='admin_delete_category'),
    path('admin/subcategories/add/', views.admin_add_subcategory, name='admin_add_subcategory'),
    path('admin/coupons/', views.admin_coupons, name='admin_coupons'),
    path('admin/coupons/add/', views.admin_add_coupon, name='admin_add_coupon'),
    path('admin/coupons/<int:coupon_id>/edit/', views.admin_edit_coupon, name='admin_edit_coupon'),
    path('admin/coupons/<int:coupon_id>/delete/', views.admin_delete_coupon, name='admin_delete_coupon'),
    path('admin/reviews/', views.admin_reviews, name='admin_reviews'),

    
    # Seller Dashboard
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/products/', views.seller_products, name='seller_products'),
    path('seller/products/add/', views.seller_add_product, name='seller_add_product'),
    path('seller/products/<int:product_id>/edit/', views.seller_edit_product, name='seller_edit_product'),
    path('seller/products/<int:product_id>/delete/', views.seller_delete_product, name='seller_delete_product'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
]
