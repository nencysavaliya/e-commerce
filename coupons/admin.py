from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount', 'times_used', 'expiry_date', 'is_active')
    list_filter = ('discount_type', 'is_active', 'expiry_date')
    search_fields = ('code',)
    list_editable = ('is_active',)
    
    actions = ['activate_coupons', 'deactivate_coupons']
    
    @admin.action(description='Activate selected coupons')
    def activate_coupons(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description='Deactivate selected coupons')
    def deactivate_coupons(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('coupon__code', 'user__username')
