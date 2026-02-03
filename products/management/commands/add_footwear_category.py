from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Add Footwear category to the database'

    def handle(self, *args, **kwargs):
        # Create or get Footwear category
        footwear_category, created = Category.objects.get_or_create(
            slug='footwear',
            defaults={
                'name': 'Footwear',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('\n✓ Successfully created "Footwear" category!'))
            self.stdout.write(f'  - ID: {footwear_category.pk}')
            self.stdout.write(f'  - Name: {footwear_category.name}')
            self.stdout.write(f'  - Slug: {footwear_category.slug}')
            self.stdout.write(f'  - Active: {footwear_category.is_active}')
        else:
            self.stdout.write(self.style.WARNING('\n✓ "Footwear" category already exists!'))
            self.stdout.write(f'  - ID: {footwear_category.pk}')
            self.stdout.write(f'  - Name: {footwear_category.name}')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('NEXT STEPS:'))
        self.stdout.write('='*60)
        self.stdout.write('1. Go to Django Admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('2. Navigate to: Products → Products')
        self.stdout.write('3. Find your footwear/shoe products (like "Canvas Shoes", etc.)')
        self.stdout.write('4. Edit each footwear product:')
        self.stdout.write('   - Change "Category" dropdown to "Footwear"')
        self.stdout.write('   - Click "Save"')
        self.stdout.write('\nAfter assigning products, the Footwear box on the home')
        self.stdout.write('page will show your footwear products!')
        self.stdout.write('='*60 + '\n')
