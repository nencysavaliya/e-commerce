from django.contrib import admin
from .models import Address, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'total_price')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'city', 'state', 'pincode', 'is_default')
    list_filter = ('state', 'city', 'is_default')
    search_fields = ('user__username', 'name', 'city', 'pincode')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'final_amount', 'payment_status', 'order_status', 'created_at')
    list_filter = ('payment_status', 'order_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'address')
        }),
        ('Amounts', {
            'fields': ('total_amount', 'discount_amount', 'final_amount')
        }),
        ('Status', {
            'fields': ('payment_status', 'order_status')
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_shipped', 'mark_as_delivered']
    
    @admin.action(description='Mark selected orders as shipped')
    def mark_as_shipped(self, request, queryset):
        queryset.update(order_status='shipped')
    
    @admin.action(description='Mark selected orders as delivered')
    def mark_as_delivered(self, request, queryset):
        queryset.update(order_status='delivered')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'price', 'total_price')
    list_filter = ('order__created_at',)
    search_fields = ('order__order_number', 'product_name')
