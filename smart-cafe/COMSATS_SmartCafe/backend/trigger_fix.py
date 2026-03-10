import requests

try:
    res = requests.get("http://127.0.0.1:5000/api/debug/fix_metadata", timeout=5)
    print(res.json())
except Exception as e:
    print("Error:", e)
