import mysql.connector
from backend.database import get_db_connection

def fix_booking_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print("Checking 'bookings' table status column...")
        # Change status column to VARCHAR(50) to support 'Deleted', 'Confirmed', etc.
        cursor.execute("ALTER TABLE bookings MODIFY COLUMN status VARCHAR(50) DEFAULT 'Pending'")
        print("✅ 'bookings' table status column updated to VARCHAR(50).")
        
        print("Checking 'orders' table status column...")
        # Do the same for orders just in case
        cursor.execute("ALTER TABLE orders MODIFY COLUMN status VARCHAR(50) DEFAULT 'Pending'")
        print("✅ 'orders' table status column updated to VARCHAR(50).")
        
        conn.commit()
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_booking_status()
