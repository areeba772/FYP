from backend.app import get_db_connection

def check_db_logic():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("--- MENU RATINGS CHECK ---")
    cursor.execute("SELECT * FROM menu_items")
    items = cursor.fetchall()
    
    for item in items:
        # Replicating logic from app.py
        cursor.execute("SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM reviews WHERE item_id=%s", (item['item_id'],))
        res = cursor.fetchone()
        rating = float(res['avg_rating']) if res['avg_rating'] else 3.0
        count = res['count'] if res['count'] else 0
        
        print(f"Item: {item['name']}, ID: {item['item_id']}, Rating: {rating}, Count: {count}")

    conn.close()

if __name__ == "__main__":
    check_db_logic()
