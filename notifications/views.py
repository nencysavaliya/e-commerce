from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import EmailLog


@staff_member_required
def email_logs(request):
    """View email logs (admin only)"""
    logs = EmailLog.objects.select_related('user').all()[:100]
    return render(request, 'notifications/email_logs.html', {'logs': logs})
