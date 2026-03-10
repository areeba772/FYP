import mysql.connector
from mysql.connector import Error


def create_reviews_table():
    try:
        connection = mysql.connector.connect(host='localhost',
                                             user='root',
                                             password='',
                                             database='comsats_smartcafe')

        if connection.is_connected():
            cursor = connection.cursor()

            # Create reviews table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(100) NOT NULL,
                item_id INT NOT NULL,
                rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                review_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES menu_items(item_id) ON DELETE CASCADE
            );
            """
            cursor.execute(create_table_query)
            print("Table 'reviews' created successfully (or already exists).")

            # Check if rating and review_count columns exist in menu_items, if not create them
            # (They likely exist based on previous errors, but good to ensure default values)

            # Update menu_items to ensure defaults if needed (optional, mainly for new logic)
            # We assume menu_items has rating and review_count.
            # Let's reset them to 0 if we want a fresh start, but better to leave existing data if any.
            # However, since the user wants "actual" reviews, we might want to recalculate if there were duplicate/fake data.
            # For now, we just ensure the table exists.

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():  # type: ignore
            cursor.close()  # type: ignore
            connection.close()  # type: ignore
            print("MySQL connection is closed")


if __name__ == "__main__":
    create_reviews_table()
