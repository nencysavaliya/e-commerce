from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import EmailLog


def send_order_confirmation_email(order):
    """Send order confirmation email"""
    subject = f'Order Confirmation - {order.order_number} | IndiVibe'
    message = f'''
    Dear {order.user.username},
    
    Thank you for your order at IndiVibe!
    
    Order Number: {order.order_number}
    Total Amount: ₹{order.final_amount}
    
    We will notify you when your order is shipped.
    
    Best regards,
    IndiVibe Team
    '''
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.user.email],
            fail_silently=True,
        )
        
        EmailLog.objects.create(
            user=order.user,
            email=order.user.email,
            subject=subject,
            message=message,
            email_type='order_confirmation',
            is_sent=True
        )
    except Exception as e:
        EmailLog.objects.create(
            user=order.user,
            email=order.user.email,
            subject=subject,
            message=message,
            email_type='order_confirmation',
            is_sent=False
        )


def send_order_shipped_email(order):
    """Send order shipped notification"""
    subject = f'Order Shipped - {order.order_number} | IndiVibe'
    message = f'''
    Dear {order.user.username},
    
    Great news! Your order {order.order_number} has been shipped.
    
    Thank you for shopping with IndiVibe!
    
    Best regards,
    IndiVibe Team
    '''
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.user.email],
            fail_silently=True,
        )
        
        EmailLog.objects.create(
            user=order.user,
            email=order.user.email,
            subject=subject,
            message=message,
            email_type='order_shipped',
            is_sent=True
        )
    except Exception:
        pass


def send_welcome_email(user):
    """Send welcome email to new users"""
    subject = 'Welcome to IndiVibe!'
    message = f'''
    Dear {user.username},
    
    Welcome to IndiVibe! We're excited to have you on board.
    
    Start exploring our amazing products and enjoy your shopping experience.
    
    Best regards,
    IndiVibe Team
    '''
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
        
        EmailLog.objects.create(
            user=user,
            email=user.email,
            subject=subject,
            message=message,
            email_type='welcome',
            is_sent=True
        )
    except Exception:
        pass
