import mysql.connector

def fix_schema():
    print("🔧 Connecting to Database...")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="areeba1012",
            database="smart_cafe_db"
        )
        cursor = conn.cursor()
        print("✅ Connected!")

        # 1. Fix 'bookings' table - Add 'table_id'
        try:
            print("Checking 'bookings' table for 'table_id'...")
            cursor.execute("SELECT table_id FROM bookings LIMIT 1")
            cursor.fetchall() # Consume results
            print("✅ 'table_id' already exists in 'bookings'.")
        except mysql.connector.Error as err:
            if err.errno == 1054: # Unknown column
                print("⚠️ 'table_id' missing in 'bookings'. Adding it...")
                cursor.execute("ALTER TABLE bookings ADD COLUMN table_id INT DEFAULT NULL")
                conn.commit()
                print("✅ 'table_id' column added successfully!")
            else:
                print(f"❌ Error checking bookings: {err}")

        # 2. Fix 'dining_tables' table - Add 'reserved_by'
        try:
            print("Checking 'dining_tables' table for 'reserved_by'...")
            cursor.execute("SELECT reserved_by FROM dining_tables LIMIT 1")
            cursor.fetchall() # Consume results
            print("✅ 'reserved_by' already exists in 'dining_tables'.")
        except mysql.connector.Error as err:
            if err.errno == 1054:
                print("⚠️ 'reserved_by' missing in 'dining_tables'. Adding it...")
                cursor.execute("ALTER TABLE dining_tables ADD COLUMN reserved_by VARCHAR(255) DEFAULT NULL")
                conn.commit()
                print("✅ 'reserved_by' column added successfully!")
            else:
                print(f"❌ Error checking dining_tables: {err}")

        cursor.close()
        conn.close()
        print("\n🎉 Database Schema Fixed! Please restart your backend server.")

    except mysql.connector.Error as err:
        print(f"❌ Connection Failed: {err}")

if __name__ == "__main__":
    fix_schema()
