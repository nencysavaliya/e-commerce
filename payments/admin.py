from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_id', 'payment_method', 'payment_status', 'amount', 'created_at')
    list_filter = ('payment_method', 'payment_status', 'created_at')
    search_fields = ('order__order_number', 'payment_id')
    readonly_fields = ('payment_id', 'razorpay_order_id', 'razorpay_signature', 'created_at', 'updated_at')
    
    actions = ['mark_as_refunded']
    
    @admin.action(description='Mark selected payments as refunded')
    def mark_as_refunded(self, request, queryset):
        queryset.update(payment_status='refunded')
