import sqlite3
import os

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get Vitamin C Serum product details
cursor.execute("""
    SELECT id, name, image, category_id, is_active 
    FROM products 
    WHERE name LIKE '%Vitamin%' 
    ORDER BY id
""")
rows = cursor.fetchall()

print("=== Vitamin C Serum Product Details ===")
for r in rows:
    print(f"ID: {r[0]}")
    print(f"Name: {r[1]}")
    print(f"Image Path in DB: [{r[2]}]")
    print(f"Category ID: {r[3]}")
    print(f"Is Active: {r[4]}")
    print("-" * 60)
    
    # Check if file exists
    if r[2]:
        file_path = os.path.join('media', r[2])
        exists = os.path.exists(file_path)
        print(f"File Path: {file_path}")
        print(f"File Exists: {exists}")
        if exists:
            size = os.path.getsize(file_path)
            print(f"File Size: {size} bytes")
    else:
        print("Image field is NULL/empty")
    print("=" * 60)

conn.close()

# Also check what files exist in media/products with vitamin/serum
print("\n=== Checking media/products for vitamin/serum files ===")
media_products = 'media/products'
if os.path.exists(media_products):
    files = os.listdir(media_products)
    matching = [f for f in files if 'vitamin' in f.lower() or 'serum' in f.lower()]
    if matching:
        print(f"Found {len(matching)} matching files:")
        for f in matching:
            full_path = os.path.join(media_products, f)
            size = os.path.getsize(full_path)
            print(f"  - {f} ({size} bytes)")
    else:
        print("No matching files found")
else:
    print(f"Directory {media_products} does not exist")
