from backend.app import get_db_connection

def check_schema():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DESCRIBE menu_items")
    rows = cursor.fetchall()
    for r in rows:
        print(r['Field'])
    conn.close()

if __name__ == "__main__":
    check_schema()
