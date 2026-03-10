from backend.app import get_db_connection

def debug_pizza():
    conn = get_db_connection()
    c = conn.cursor(dictionary=True)
    
    print("--- MENU ITEMS (Pizza) ---")
    c.execute("SELECT item_id, name, review_count FROM menu_items WHERE name LIKE '%Pizza%'")
    items = c.fetchall()
    print(items)
    
    if not items:
        print("No item found with 'Pizza' in name.")
        conn.close()
        return

    print("\n--- REVIEWS (Pizza) ---")
    # Check by Name
    c.execute("SELECT count(*) as count FROM reviews WHERE item_name LIKE '%Pizza%'")
    print("Count by Name:", c.fetchone())
    
    # Check by ID for first match
    if items:
        pid = items[0]['item_id']
        c.execute("SELECT count(*) as count FROM reviews WHERE item_id = %s", (pid,))
        print(f"Count by ID ({pid}):", c.fetchone())

    conn.close()

if __name__ == "__main__":
    debug_pizza()
