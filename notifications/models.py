from django.db import models
from django.conf import settings


class EmailLog(models.Model):
    """Email log model to track sent emails"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_logs', null=True, blank=True)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    email_type = models.CharField(max_length=50, blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_logs'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f'{self.subject} to {self.email}'
