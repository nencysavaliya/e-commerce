"""
Script to add Footwear category to the IndiVibe e-commerce database
Run this with: python add_footwear_category.py
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

try:
    django.setup()
    from products.models import Category
    
    # Create or get Footwear category
    footwear_category, created = Category.objects.get_or_create(
        slug='footwear',
        defaults={
            'name': 'Footwear',
            'is_active': True,
        }
    )
    
    if created:
        print("✓ Successfully created 'Footwear' category!")
        print(f"  - ID: {footwear_category.pk}")
        print(f"  - Name: {footwear_category.name}")
        print(f"  - Slug: {footwear_category.slug}")
        print(f"  - Active: {footwear_category.is_active}")
    else:
        print("✓ 'Footwear' category already exists!")
        print(f"  - ID: {footwear_category.pk}")
        print(f"  - Name: {footwear_category.name}")
    
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("="*50)
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to: Products → Products")
    print("3. Find your footwear/shoe products")
    print("4. Edit each footwear product:")
    print("   - Change 'Category' to 'Footwear'")
    print("   - Click 'Save'")
    print("\nAfter assigning products, the Footwear box on")
    print("the home page will show your footwear products!")
    print("="*50)
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nTrying alternative method...")
    print("\nPlease add the category manually:")
    print("1. Visit: http://127.0.0.1:8000/admin/")
    print("2. Go to: Products → Categories → Add Category")
    print("3. Fill in:")
    print("   - Name: Footwear")
    print("   - Slug: footwear")
    print("   - Check: Is active")
    print("4. Click SAVE")
