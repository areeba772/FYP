from backend.app import get_db_connection

def fix_review_links():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print("--- FIXING REVIEW LINKS ---")
    
    # Get all menu items
    cursor.execute("SELECT item_id, name FROM menu_items")
    menu = cursor.fetchall()
    
    updates = 0
    for item in menu:
        # Update reviews where name matches but item_id is NULL
        # Or even force update all to be safe
        query = "UPDATE reviews SET item_id = %s WHERE item_name = %s"
        cursor.execute(query, (item['item_id'], item['name']))
        updates += cursor.rowcount
        
    conn.commit()
    print(f"Updated {updates} review records with correct item_id.")
    
    # Verify
    cursor.execute("SELECT item_name, item_id, rating FROM reviews LIMIT 10")
    print(cursor.fetchall())
    
    conn.close()

if __name__ == "__main__":
    fix_review_links()
