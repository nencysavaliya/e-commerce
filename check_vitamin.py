import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check Vitamin C Serum product
cursor.execute("SELECT id, name, image FROM products WHERE name LIKE '%Vitamin%' OR name LIKE '%Serum%'")
rows = cursor.fetchall()

print("Products matching Vitamin or Serum:")
print("-" * 80)
for r in rows:
    print(f"ID: {r[0]} | Name: {r[1]} | Image: [{r[2]}]")

conn.close()
