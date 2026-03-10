from backend.app import get_db_connection
import sys

def debug_to_file():
    with open("debug_out.txt", "w") as f:
        try:
            conn = get_db_connection()
            c = conn.cursor(dictionary=True)
            
            f.write("--- MENU ITEMS ---\n")
            c.execute("SELECT item_id, name FROM menu_items WHERE name LIKE '%Pizza%'")
            items = c.fetchall()
            f.write(str(items) + "\n")
            
            if items:
                pid = items[0]['item_id']
                pname = items[0]['name']
                
                f.write(f"\n--- REVIEWS (ID: {pid}, Name: {pname}) ---\n")
                c.execute("SELECT item_id, item_name, rating FROM reviews WHERE item_name LIKE '%Pizza%' OR item_id = %s", (pid,))
                revs = c.fetchall()
                f.write(str(revs) + "\n")
                
                # Check mismatch count
                c.execute("SELECT count(*) as c FROM reviews WHERE item_name = %s AND (item_id IS NULL OR item_id != %s)", (pname, pid))
                mismatch = c.fetchone()['c']
                f.write(f"\nMismatched IDs for {pname}: {mismatch}\n")
                
            conn.close()
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    debug_to_file()
