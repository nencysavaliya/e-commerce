from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('generate/<int:order_id>/', views.generate_invoice, name='generate'),
    path('download/<int:invoice_id>/', views.download_invoice, name='download'),
]
