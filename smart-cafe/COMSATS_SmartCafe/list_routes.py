from backend.app import app

def list_routes():
    print("Listing all routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")

if __name__ == '__main__':
    list_routes()
