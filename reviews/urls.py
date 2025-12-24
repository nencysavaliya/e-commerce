from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:product_id>/', views.add_review, name='add'),
    path('delete/<int:review_id>/', views.delete_review, name='delete'),
    path('product/<int:product_id>/', views.product_reviews, name='product_reviews'),
]
