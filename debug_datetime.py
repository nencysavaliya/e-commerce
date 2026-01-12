from datetime import datetime

# Simulating what happens in the code
expiry_date_str = "2026-01-15 18:29:00"
expiry_date = datetime.fromisoformat(expiry_date_str)

print(f"Expiry Date: {expiry_date}")
print(f"Type: {type(expiry_date)}")
print(f"Is aware: {expiry_date.tzinfo is not None}")
print(f"Date: {expiry_date.date()}")
print("✅ No error with .date()")
