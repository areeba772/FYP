import mysql.connector

def fix_db_enum():
    print("🔧 Connecting to Database to fix ENUM...")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="areeba1012",
            database="smart_cafe_db"
        )
        cursor = conn.cursor()

        # 1. Fix 'dining_tables' status
        # The error "Data truncated" happens because 'Reserved' is not in ENUM('Available', 'Occupied')
        try:
            print("Updating 'dining_tables' status options...")
            cursor.execute("ALTER TABLE dining_tables MODIFY COLUMN status ENUM('Available', 'Occupied', 'Reserved') DEFAULT 'Available'")
            print("✅ 'dining_tables' fixed! Added 'Reserved' option.")
        except mysql.connector.Error as err:
            print(f"⚠️ Error updating dining_tables: {err}")

        # 2. Fix 'bookings' status (Just in case)
        try:
            print("Updating 'bookings' status to allow 'Confirmed'...")
            # Changing to VARCHAR to be safe, or we can expand the ENUM
            cursor.execute("ALTER TABLE bookings MODIFY COLUMN status VARCHAR(50) DEFAULT 'Pending'")
            print("✅ 'bookings' status fixed (converted to VARCHAR for flexibility).")
        except mysql.connector.Error as err:
            print(f"⚠️ Error updating bookings: {err}")

        conn.commit()
        cursor.close()
        conn.close()
        print("\n🎉 Database Fixed! You can now book tables.")

    except mysql.connector.Error as err:
        print(f"❌ Connection Failed: {err}")

if __name__ == "__main__":
    fix_db_enum()
