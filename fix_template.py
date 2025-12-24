import os

# Read the checkout.html file
file_path = r'd:\practic-project\e-commerce\templates\orders\checkout.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken template tag for total amount (lines 151-152)
# Find and replace the broken tag split across lines
content = content.replace(
    '₹{{\r\n                    final_amount|default:cart.subtotal }}',
    '₹{{ final_amount|default:cart.subtotal }}'
)

# Also try without \r in case line endings are different
content = content.replace(
    '₹{{\n                    final_amount|default:cart.subtotal }}',
    '₹{{ final_amount|default:cart.subtotal }}'
)

# Fix the address default check (lines 22-23)
content = content.replace(
    '{% if addr.is_default\r\n                                %}checked',
    '{% if addr.is_default %}checked'
)

content = content.replace(
    '{% if addr.is_default\n                                %}checked',
    '{% if addr.is_default %}checked'
)

# Write the fixed content back
with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print("Fixed checkout.html template tags!")
