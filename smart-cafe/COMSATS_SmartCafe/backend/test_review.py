import requests
import json

url = "http://127.0.0.1:5000/api/submit_review"

# 1. Login/Get User (Need a valid email in DB)
# Assuming 'areeba@example.com' or similar exists. 
# We'll valid email from previous context or generic one.
email = "test@user.com"

payload = {
    "email": email,
    "item_name": "Zinger Burger", # Must match a real item name in menu_items
    "rating": 5,
    "comment": "Test review with auto-injected item name",
    "order_id": 9999
}

try:
    res = requests.post(url, json=payload)
    print(res.status_code)
    print(res.json())
except Exception as e:
    print(e)
