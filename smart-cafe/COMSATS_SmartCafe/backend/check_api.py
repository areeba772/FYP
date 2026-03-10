import requests
import json

try:
    print("Fetching /api/menu...")
    res = requests.get("http://127.0.0.1:5000/api/menu")
    data = res.json()
    
    if data['success']:
        print(f"Found {len(data['menu'])} items.")
        print("Top 3 Items:")
        for item in data['menu'][:3]:
            print(f"Name: {item['name']}, Rating: {item.get('rating')}, Count: {item.get('review_count')}")
    else:
        print("API Failed:", data)

except Exception as e:
    print("Error:", e)
