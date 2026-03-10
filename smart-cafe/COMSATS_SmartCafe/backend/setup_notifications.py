import mysql.connector

def create_notifications_table():
    print("🔧 Connecting to Database...")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="areeba1012",
            database="smart_cafe_db"
        )
        cursor = conn.cursor()
        
        # Create Notifications Table
        query = """
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            is_read TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(query)
        print("✅ 'notifications' table created successfully!")

        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"❌ Connection Failed: {err}")

if __name__ == "__main__":
    create_notifications_table()
