from backend.app import get_db_connection, app

def debug_reviews():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("--- 1. CURRENT REVIEWS DATA ---")
    cursor.execute("SELECT review_id, item_name, rating FROM reviews")
    rows = cursor.fetchall()
    for r in rows:
        print(r)

    print("\n--- 2. UPDATING NULLS ---")
    cursor.execute("UPDATE reviews SET item_name='Legacy Item' WHERE item_name IS NULL OR item_name = ''")
    conn.commit()
    print(f"Updated {cursor.rowcount} rows.")

    print("\n--- 3. VERIFYING UPDATE ---")
    cursor.execute("SELECT review_id, item_name FROM reviews")
    rows = cursor.fetchall()
    for r in rows:
        print(r)
        
    conn.close()

if __name__ == "__main__":
    debug_reviews()
