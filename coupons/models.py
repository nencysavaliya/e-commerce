from django.db import models
from django.conf import settings


class Coupon(models.Model):
    """Coupon model"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('flat', 'Flat Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(default=0, help_text='0 for unlimited')
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupons'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
    
    def __str__(self):
        return self.code
    
    @property
    def times_used(self):
        return self.usages.count()
    
    def is_valid(self, user=None, order_amount=0):
        """Check if coupon is valid"""
        from django.utils import timezone
        
        if not self.is_active:
            return False, 'Coupon is not active'
        
        if self.expiry_date < timezone.now():
            return False, 'Coupon has expired'
        
        if self.usage_limit > 0 and self.times_used >= self.usage_limit:
            return False, 'Coupon usage limit reached'
        
        if order_amount < self.min_order_amount:
            return False, f'Minimum order amount is ₹{self.min_order_amount}'
        
        if user and CouponUsage.objects.filter(coupon=self, user=user).exists():
            return False, 'You have already used this coupon'
        
        return True, 'Coupon is valid'
    
    def calculate_discount(self, order_amount):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            discount = (order_amount * self.discount_value) / 100
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = self.discount_value
        return min(discount, order_amount)


class CouponUsage(models.Model):
    """Track coupon usage"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_usages')
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupon_usages'
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        unique_together = ['coupon', 'user']
    
    def __str__(self):
        return f'{self.user.username} used {self.coupon.code}'
