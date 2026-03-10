import mysql.connector
from backend.database import get_db_connection
import time

def force_fix():
    print("Connecting to database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Check current status
        print("Checking current 'bookings' schema...")
        cursor.execute("DESCRIBE bookings")
        columns = cursor.fetchall()
        for col in columns:
            if col[0] == 'status':
                print(f"Current 'status' column definition: {col[1]}")

        # 2. Force Update
        print("Attempting to ALTER 'bookings' status to VARCHAR(50)...")
        try:
            cursor.execute("ALTER TABLE bookings MODIFY COLUMN status VARCHAR(50) NOT NULL DEFAULT 'Pending'")
            conn.commit()
            print("ALTERNATION COMMAND EXECUTED.")
        except Exception as e:
            print(f"Alter failed: {e}")

        # 3. Verify
        print("Verifying schema after update...")
        cursor.execute("DESCRIBE bookings")
        columns = cursor.fetchall()
        for col in columns:
            if col[0] == 'status':
                print(f"New 'status' column definition: {col[1]}")

        # 4. Check Orders as well
        print("Checking 'orders' schema...")
        cursor.execute("DESCRIBE orders")
        columns = cursor.fetchall()
        for col in columns:
             if col[0] == 'status':
                print(f"Current 'orders' status column definition: {col[1]}")
        
        print("Attempting to ALTER 'orders' status to VARCHAR(50)...")
        try:
             cursor.execute("ALTER TABLE orders MODIFY COLUMN status VARCHAR(50) NOT NULL DEFAULT 'Pending'")
             conn.commit()  
             print("ORDERS ALTERNATION COMMAND EXECUTED.")
        except Exception as e:
             print(f"Order Alter failed: {e}")


    except Exception as e:
        print(f"General Error: {e}")
    finally:
        cursor.close()
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    force_fix()
