from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('user__username', 'product__name', 'review_text')
    list_editable = ('is_approved',)
    
    actions = ['approve_reviews', 'hide_reviews']
    
    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    
    @admin.action(description='Hide selected reviews')
    def hide_reviews(self, request, queryset):
        queryset.update(is_approved=False)
