from django.contrib import admin
from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'email_type', 'is_sent', 'sent_at')
    list_filter = ('is_sent', 'email_type', 'sent_at')
    search_fields = ('email', 'subject')
    readonly_fields = ('user', 'email', 'subject', 'message', 'email_type', 'is_sent', 'sent_at')
