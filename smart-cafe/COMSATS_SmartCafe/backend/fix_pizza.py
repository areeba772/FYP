from backend.app import get_db_connection

def fix_pizza():
    conn = get_db_connection()
    c = conn.cursor(dictionary=True)
    
    # 1. Get Pizza ID
    c.execute("SELECT item_id, name FROM menu_items WHERE name LIKE '%Pizza%'")
    pizza = c.fetchone()
    
    if pizza:
        pid = pizza['item_id']
        pname = pizza['name']
        print(f"Found {pname} with ID: {pid}")
        
        # 2. Update Reviews
        c.execute("UPDATE reviews SET item_id = %s WHERE item_name LIKE '%Pizza%'", (pid,))
        conn.commit()
        print(f"Updated {c.rowcount} reviews for Pizza.")
    else:
        print("Pizza item not found in menu!")

    conn.close()

if __name__ == "__main__":
    fix_pizza()
