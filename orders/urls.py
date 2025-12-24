from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('add-address/', views.add_address, name='add_address'),
    path('history/', views.order_history, name='order_history'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
]
