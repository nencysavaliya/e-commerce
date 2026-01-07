import os
import django
import sqlite3

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce_project.settings")
django.setup()

from products.models import Product

# Connect to local SQLite DB
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute("""
SELECT id, category_id, subcategory_id, seller_id, name, slug, description,
       price, discount_price, stock, image, is_active, is_featured, created_at, updated_at
FROM products
""")
rows = cursor.fetchall()

migrated_count = 0
for row in rows:
    try:
        Product.objects.update_or_create(
            id=row[0],
            defaults={
                'category_id': row[1],
                'subcategory_id': row[2],
                'seller_id': row[3],
                'name': row[4],
                'slug': row[5],
                'description': row[6],
                'price': row[7],
                'discount_price': row[8],
                'stock': row[9],
                'image': row[10],
                'is_active': row[11],
                'is_featured': row[12],
                'created_at': row[13],
                'updated_at': row[14],
            }
        )
        migrated_count += 1
    except Exception as e:
        print(f"Error migrating product {row[0]}: {e}")

conn.close()
print(f"\n✅ Total products migrated: {migrated_count}")
