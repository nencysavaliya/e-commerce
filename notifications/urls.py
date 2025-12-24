from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('email-logs/', views.email_logs, name='email_logs'),
]
