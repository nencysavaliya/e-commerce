import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get first 10 products ordered by created_at DESC (latest first)
cursor.execute("""
    SELECT id, name, image, created_at
    FROM products 
    ORDER BY created_at DESC
    LIMIT 10
""")
rows = cursor.fetchall()

print("=== First 10 Products (by created_at DESC) ===")
for i, r in enumerate(rows, 1):
    print(f"{i}. ID:{r[0]} | Name: {r[1][:30]:30} | Image: {r[2][:40] if r[2] else 'NULL'}")

print("\n" + "=" * 80)

# Get Vitamin C Serum specifically
cursor.execute("""
    SELECT id, name, image, created_at, is_active
    FROM products 
    WHERE name LIKE '%Vitamin%'
""")
rows = cursor.fetchall()

print("\n=== Vitamin C Serum Details ===")
for r in rows:
    print(f"ID: {r[0]}")
    print(f"Name: {r[1]}")
    print(f"Image: '{r[2]}'")
    print(f"Created: {r[3]}")
    print(f"Active: {r[4]}")

conn.close()
