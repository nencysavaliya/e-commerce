from django.db import models
from orders.models import Order


class Invoice(models.Model):
    """Invoice model for orders"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f'INV-{self.order.order_number}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.invoice_number
