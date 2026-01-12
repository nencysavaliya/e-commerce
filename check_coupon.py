import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get SAVE20 coupon
cursor.execute("SELECT code, expiry_date, is_active FROM coupons WHERE code='SAVE20'")
result = cursor.fetchone()

if result:
    code, expiry_date, is_active = result
    print(f"Coupon Code: {code}")
    print(f"Expiry Date (DB): {expiry_date}")
    print(f"Is Active: {is_active}")
    print(f"Current DateTime: {datetime.now()}")
    
    # Parse the datetime
    if expiry_date:
        expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
        current_dt = datetime.now()
        print(f"\nParsed Expiry: {expiry_dt}")
        print(f"Current Time: {current_dt}")
        print(f"Is Expired: {expiry_dt < current_dt}")
else:
    print("SAVE20 coupon not found!")

conn.close()
