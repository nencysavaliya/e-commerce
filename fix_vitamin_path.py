import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Update the image path to include products/ prefix
cursor.execute("""
    UPDATE products 
    SET image = 'products/vitamin-c-serum.jpeg'
    WHERE id = 70 AND name = 'Vitamin C Serum'
""")

conn.commit()
print(f"Updated {cursor.rowcount} row(s)")

# Verify the update
cursor.execute("SELECT id, name, image FROM products WHERE id = 70")
row = cursor.fetchone()
print(f"\nVerification:")
print(f"ID: {row[0]}")
print(f"Name: {row[1]}")
print(f"Image: '{row[2]}'")

conn.close()
