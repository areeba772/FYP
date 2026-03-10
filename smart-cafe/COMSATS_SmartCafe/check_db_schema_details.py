import mysql.connector
from backend.database import get_db_connection

def check_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print("--- BOOKINGS TABLE SCHEMA ---")
        cursor.execute("DESCRIBE bookings")
        for row in cursor.fetchall():
            print(row)
            
        print("\n--- ORDERS TABLE SCHEMA ---")
        cursor.execute("DESCRIBE orders")
        for row in cursor.fetchall():
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_schema()
