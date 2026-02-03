# Generated data migration for adding Footwear category

from django.db import migrations


def add_footwear_category(apps, schema_editor):
    """Add Footwear category to the database"""
    Category = apps.get_model('products', 'Category')
    
    # Create Footwear category if it doesn't exist
    Category.objects.get_or_create(
        slug='footwear',
        defaults={
            'name': 'Footwear',
            'is_active': True,
        }
    )


def remove_footwear_category(apps, schema_editor):
    """Remove Footwear category (reverse operation)"""
    Category = apps.get_model('products', 'Category')
    Category.objects.filter(slug='footwear').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_image'),
    ]

    operations = [
        migrations.RunPython(add_footwear_category, remove_footwear_category),
    ]
