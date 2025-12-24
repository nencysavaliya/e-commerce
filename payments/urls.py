from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:order_id>/', views.initiate_payment, name='initiate'),
    path('callback/', views.payment_callback, name='callback'),
    path('cod/<int:order_id>/', views.cod_payment, name='cod'),
    path('success/<int:order_id>/', views.payment_success, name='success'),
    path('failed/<int:order_id>/', views.payment_failed, name='failed'),
]
