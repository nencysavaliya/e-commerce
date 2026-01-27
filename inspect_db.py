import sqlite3
import sys

# Connect to database  
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("=== All Tables in Database ===")
for table in tables:
    print(f"  - {table[0]}")

# Check if core_student exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_student';")
student_table = cursor.fetchone()

if student_table:
    print("\n=== core_student table schema ===")
    cursor.execute(f"PRAGMA table_info(core_student);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - NotNull: {col[3]}, Default: {col[4]}, PK: {col[5]}")

conn.close()
