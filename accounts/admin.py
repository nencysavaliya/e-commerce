from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_seller', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_seller', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('IndiVibe Fields', {
            'fields': ('is_seller', 'phone', 'profile_image')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('IndiVibe Fields', {
            'fields': ('email', 'is_seller', 'phone')
        }),
    )
    
    actions = ['make_seller', 'remove_seller', 'block_users', 'unblock_users']
    
    @admin.action(description='Make selected users sellers')
    def make_seller(self, request, queryset):
        queryset.update(is_seller=True)
    
    @admin.action(description='Remove seller status')
    def remove_seller(self, request, queryset):
        queryset.update(is_seller=False)
    
    @admin.action(description='Block selected users')
    def block_users(self, request, queryset):
        queryset.update(is_active=False)
    
    @admin.action(description='Unblock selected users')
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)
