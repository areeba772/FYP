from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import mysql.connector
from typing import Optional, List, Dict, Any, cast
from flask_cors import CORS
import re

# Try importing AI engine, if missing, skip it to prevent crash
try:
    from ml_model import get_smart_recommendations  # type: ignore
except ImportError:
    print("⚠️ AI Engine not found. Recommendations will not work.")

    def get_smart_recommendations(menu, item):
        return []


# Set template and static folders to point to frontend directory
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = 'super_secret_key_areeba_cafe'  # Session/Flash required
CORS(app)


# --- 1. DATABASE CONNECTION (CENTRALIZED) ---
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="areeba1012",
        database="smart_cafe_db",
        buffered=True  # <--- SIRF YEH ADD KAREIN
    )
    return conn


# --- 2. HOME ROUTE ---
@app.route('/')
def home():
    return render_template('index.html')


# ==========================================
#               USER API ROUTES
# ==========================================


# --- SIGNUP ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json

    # --- VALIDATION RULE 1: Name must be Alphabets Only ---
    if not re.match(r"^[A-Za-z\s]+$", data.get('name', '')):
        return jsonify({
            "success": False,
            "message": "Name must contain alphabets only!"
        }), 400

    # --- VALIDATION RULE 2: Password must be 6 Digits Only ---
    if not re.match(r"^\d{6}$", data.get('password', '')):
        return jsonify({
            "success": False,
            "message": "Password must be exactly 6 digits!"
        }), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({
            "success": False,
            "message": "DB Error"
        }), 500  # noqa: E701
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s",
                       (data['email'], ))
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "User already exists!"
            }), 400

        query = "INSERT INTO users (full_name, email, password, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (data['name'], data['email'], data['password'],
                               'user'))  # Auto-assign 'user' role
        conn.commit()
        return jsonify({"success": True, "message": "Account Created!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- LOGIN ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "success": False,
            "message": "DB Error"
        }), 500  # noqa: E701
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (data['email'], data['password']))
        user = cursor.fetchone()
        if user:
            # Set session based on role
            if user['role'] == 'admin':  # type: ignore
                session['user_role'] = 'admin'
                session['admin_logged_in'] = True
                session['user_email'] = user['email']  # type: ignore
            elif user['role'] == 'authority':  # type: ignore
                session['user_role'] = 'authority'
                session['authority_logged_in'] = True
                session['user_email'] = user['email']  # type: ignore
            else:
                session['user_role'] = 'user'
                session['user_email'] = user['email']  # type: ignore

            return jsonify({
                "success": True,
                "message": "Login Successful!",
                "name": user['full_name'],  # type: ignore
                "role": user['role']  # type: ignore
            })
        else:
            return jsonify({
                "success": False,
                "message": "Invalid Credentials"
            }), 401
    finally:
        cursor.close()
        conn.close()


# --- GET MENU ---
@app.route('/api/menu', methods=['GET'])
def get_menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # type: ignore
    
    # Fetch all menu items
    cursor.execute("SELECT * FROM menu_items")
    menu = cursor.fetchall()

    # Inject Ratings into menu items
    for item in menu:
        cursor.execute(
            "SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM reviews WHERE item_id=%s",
            (item['item_id'], ))
        res_r = cast(Dict[str, Any], cursor.fetchone())
        if res_r and res_r.get('count', 0) > 0:
            item['rating'] = float(res_r['avg_rating']) if res_r.get('avg_rating') else 0.0
            item['review_count'] = res_r['count']
        else:
            item['rating'] = 0.0
            item['review_count'] = 0

    cursor.close()
    conn.close()  # type: ignore
    return jsonify({"success": True, "menu": menu})


# --- PLACE ORDER (Enhanced with Table Number and Guests) ---
@app.route('/api/place_order', methods=['POST'])
def place_order():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()  # type: ignore
    try:
        # Check User
        cursor.execute("SELECT user_id FROM users WHERE email = %s",
                       (data['email'], ))
        user_row = cursor.fetchone()
        if not user_row:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        user_id = user_row[0]

        # Update Name if provided from the fronted Form
        if data.get('name'):
            cursor.execute(
                "UPDATE users SET full_name = %s WHERE user_id = %s",
                (data['name'], user_id))

        if 'Phone: ' in data.get('address', ''):
            extracted_phone = data['address'].split('Phone: ')[1].strip()
            if extracted_phone:
                cursor.execute(
                    "UPDATE users SET phone = %s WHERE user_id = %s",
                    (extracted_phone, user_id))

        # Payment Status
        pay_status = "Pending"
        if data.get('paymentMethod') == "JazzCash" and data.get(
                'transaction_id'):
            # User wants JazzCash to be treated as paid when Transaction ID is provided
            pay_status = "Paid"

        # Insert Order with table number and guests for dine-in
        query = """INSERT INTO orders (user_id, total_amount, payment_method, delivery_address, 
                   status, transaction_id, payment_status, table_number, number_of_guests, order_type) 
                   VALUES (%s, %s, %s, %s, 'Pending', %s, %s, %s, %s, %s)"""
        cursor.execute(
            query,
            (user_id, data['total'], data['paymentMethod'],
             data.get('address', ''), data.get('transaction_id'), pay_status,
             data.get('tableNumber'), data.get('numberOfGuests'),
             data.get('orderType', 'Dine-in')))
        order_id = cursor.lastrowid

        # Insert Details
        for item in data['items']:
            cursor.execute(
                "SELECT item_id, price FROM menu_items WHERE name = %s",
                (item['name'], ))
            item_row = cursor.fetchone()
            if item_row:
                # Cast to ensure Pylance knows these are valid types
                i_id, i_price = item_row[0], item_row[1]
                cursor.execute(
                    "INSERT INTO order_details (order_id, item_id, quantity, price_at_time) VALUES (%s, %s, %s, %s)",
                    (order_id, i_id, item['qty'], i_price))

        conn.commit()

        # Create notification for user
        try:
            cursor.execute("SELECT email FROM users WHERE user_id = %s",
                           (user_id, ))
            user_email_row = cursor.fetchone()
            if user_email_row:
                user_email = user_email_row[0]
                cursor.execute(
                    "INSERT INTO notifications (user_email, message, type) VALUES (%s, %s, 'Order')",
                    (user_email,
                     f"✅ Your order #{order_id} has been placed successfully! Status: Pending"
                     ))
                conn.commit()
        except Exception as notif_error:
            print(f"Notification error: {notif_error}"
                  )  # Don't fail order if notification fails

        return jsonify({
            "success": True,
            "message": "Order Placed Successfully!",
            "order_id": order_id
        })
    except Exception as e:
        conn.rollback()
        print(f"Order placement error: {e}")  # Debug log
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# --- BOOK TABLE (Enhanced) ---
@app.route('/api/book_table', methods=['POST'])
def book_table():
    data = request.json

    # --- TIME VALIDATION (8 AM - 5 PM) ---
    booking_time = data.get('time')  # "14:30"
    if booking_time:
        hour = int(booking_time.split(':')[0])
        # Allow 08:00 to 17:00 (5 PM)
        if hour < 8 or hour >= 17:
            return jsonify({
                "success":
                False,
                "message":
                "Booking only allowed between 8 AM - 5 PM!"
            }), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if table already booked
        cursor.execute(
            "SELECT * FROM bookings WHERE booking_date = %s AND booking_time = %s AND table_id = %s AND status != 'Cancelled'",
            (data['date'], data['time'], data['tableId']))
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Table already booked for this time!"
            }), 409



        cursor.execute("SELECT user_id FROM users WHERE email = %s",
                       (data['email'], ))
        user_row = cursor.fetchone()
        if not user_row:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        user_id = user_row[0]

        cursor.execute(
            "INSERT INTO bookings (user_id, booking_date, booking_time, guests, status, table_id) VALUES (%s, %s, %s, %s, 'Confirmed', %s)",
            (user_id, data['date'], data['time'], data['people'],
             data['tableId']))



        conn.commit()
        return jsonify({"success": True, "message": "Table Reserved!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- CHECK AVAILABILITY (New) ---
@app.route('/api/check_availability', methods=['POST'])
def check_availability():
    data = request.json
    date = data.get('date')
    time = data.get('time')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Find all BOOKED tables for this slot
        query = "SELECT table_id FROM bookings WHERE booking_date = %s AND booking_time = %s AND status != 'Cancelled'"
        cursor.execute(query, (date, time))
        booked_rows = cursor.fetchall()
        booked_ids = set([row['table_id'] for row in booked_rows])



        return jsonify({"success": True, "booked_tables": list(booked_ids)})
    finally:
        cursor.close()
        conn.close()


# --- AI RECOMMENDATIONS (Logic Update) ---
@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM menu_items")
        all_menu = cursor.fetchall()

        # --- NEW: Inject Ratings into all_menu for AI ---
        for item in all_menu:
            cursor.execute(
                "SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM reviews WHERE item_id=%s",
                (item['item_id'], ))
            res_r = cast(Dict[str, Any],
                         cursor.fetchone())  # Type cast for Pylance
            if res_r:
                item['rating'] = float(res_r['avg_rating']) if res_r.get(
                    'avg_rating'
                ) else 3.0  # Default to 3 so AI picks it up if no history
                item['review_count'] = res_r['count'] if res_r.get(
                    'count') else 0
            else:
                item['rating'] = 3.0
                item['review_count'] = 0

        # Sort by Rating so high rated items are first in fallback list
        all_menu.sort(key=lambda x: x['rating'], reverse=True)
        # ------------------------------------------------

        last_item = None
        user_email = data.get('email')
        past_orders = []

        if user_email:
            # Check history
            cursor.execute(
                """SELECT mi.name, mi.image_url, mi.price, mi.item_id 
                   FROM order_details od 
                   JOIN orders o ON od.order_id = o.order_id 
                   JOIN users u ON o.user_id = u.user_id 
                   JOIN menu_items mi ON od.item_id = mi.item_id 
                   WHERE u.email = %s ORDER BY o.created_at DESC""",
                (user_email, ))
            past_orders_raw = cursor.fetchall()
            if past_orders_raw:
                last_item = past_orders_raw[0]['name']
                # Create a set to deduplicate but keep order, or just filter
                seen_names = set()
                for po in past_orders_raw:
                    if po['name'] not in seen_names:
                        # Find rating and review count from all_menu to match the structure
                        matching_item = next((item for item in all_menu if item['name'] == po['name']), None)
                        if matching_item:
                            po['rating'] = matching_item.get('rating', 3.0)
                            po['review_count'] = matching_item.get('review_count', 0)
                        else:
                            po['rating'] = 3.0
                            po['review_count'] = 0
                        past_orders.append(po)
                        seen_names.add(po['name'])

        recs = get_smart_recommendations(all_menu, last_item)

        return jsonify({"success": True, "recommendations": recs, "past_orders": past_orders})
    finally:
        cursor.close()
        conn.close()


# --- MY ORDERS ---
@app.route('/api/my_orders', methods=['POST'])
def my_orders():
    email = request.json.get('email')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """SELECT o.order_id, o.total_amount, o.status, o.created_at,
                      o.payment_method, o.payment_status, o.transaction_id
               FROM orders o JOIN users u ON o.user_id = u.user_id 
               WHERE u.email = %s ORDER BY o.created_at DESC"""
    cursor.execute(query, (email, ))
    orders = cursor.fetchall()

    for order in orders:
        cursor.execute(
            """SELECT mi.name, mi.image_url, od.quantity, od.price_at_time 
                          FROM order_details od JOIN menu_items mi ON od.item_id = mi.item_id 
                          WHERE od.order_id = %s""", (order['order_id'], ))
        order['items'] = cursor.fetchall()
        order['created_at'] = str(
            order['created_at'])  # Convert date to string

    cursor.close()
    conn.close()
    return jsonify({"success": True, "orders": orders})


# --- MY BOOKINGS (New Route for User Dashboard) ---
@app.route('/api/my_bookings', methods=['POST'])
def my_bookings():
    data = request.json
    email = data.get('email')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT b.booking_id, b.booking_date, b.booking_time, b.guests, b.status, b.table_id
            FROM bookings b JOIN users u ON b.user_id = u.user_id 
            WHERE u.email = %s ORDER BY b.booking_date DESC
        """, (email, ))
        bookings = cursor.fetchall()
        # Convert date objects to strings
        for b in bookings:
            b['booking_date'] = str(b['booking_date'])
            b['booking_time'] = str(b['booking_time'])

        return jsonify({"success": True, "bookings": bookings})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- USER: RELEASE TABLE (Mark Available) ---
@app.route('/api/user/free_table', methods=['POST'])
def user_free_table():
    data = request.json or {}
    email = data.get('email')
    table_id = data.get('table_id')

    if not email or not table_id:
        return jsonify({
            "success": False,
            "message": "email and table_id required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT full_name FROM users WHERE email=%s", (email, ))
        u = cursor.fetchone()
        if not u:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        full_name = u['full_name']



        # Mark latest active booking for this table/user as Completed (optional but helpful)
        cursor.execute(
            """
            UPDATE bookings b
            JOIN users u ON b.user_id = u.user_id
            SET b.status='Completed'
            WHERE u.email=%s AND b.table_id=%s AND b.status='Confirmed'
            ORDER BY b.booking_date DESC, b.booking_time DESC
            LIMIT 1
            """, (email, table_id))

        conn.commit()
        return jsonify({"success": True, "message": "Table released"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- CONTACT & MESSAGES ---
@app.route('/api/contact', methods=['POST'])
def contact_message():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        user_id = None
        if data.get('email'):
            cursor.execute("SELECT user_id FROM users WHERE email = %s",
                           (data['email'], ))
            row = cursor.fetchone()
            if row: user_id = row[0]
        cursor.execute(
            "INSERT INTO messages (user_id, subject, message, status) VALUES (%s, %s, %s, 'Open')",
            (user_id, data['subject'], data['message']))
        conn.commit()
        return jsonify({"success": True, "message": "Sent!"})
    finally:
        cursor.close()
        conn.close()


@app.route('/api/my_messages', methods=['POST'])
def my_messages():
    email = request.json.get('email')  # Pehle email nikal lein
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check karein ke column names bilkul sahi hain (admin_reply)
    cursor.execute(
        """SELECT m.subject, m.message, m.admin_reply, m.created_at 
           FROM messages m JOIN users u ON m.user_id = u.user_id 
           WHERE u.email = %s ORDER BY m.created_at DESC""", (email, ))

    msgs = cursor.fetchall()  # Data fetch kiya
    cursor.close()
    conn.close()

    # Yahan 'messages' key hi use karein taake JS ko mil jaye
    return jsonify({"success": True, "messages": msgs})


# ==========================================
#               ADMIN API ROUTES
# ==========================================


# --- 1. ADMIN DASHBOARD STATS ---
@app.route('/api/admin/stats')
def get_admin_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Revenue
    cursor.execute(
        "SELECT SUM(total_amount) FROM orders WHERE status != 'Cancelled'")
    res = cursor.fetchone()
    revenue = int(res[0]) if res and res[0] else 0

    # 2. Total Users (Count ALL users except the Admin himself)
    cursor.execute("SELECT COUNT(*) FROM users WHERE role != 'admin'")
    users = cursor.fetchone()[0]

    # 3. Pending Orders
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'")
    pending = cursor.fetchone()[0]

    # 4. Total Orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return jsonify({
        "revenue": revenue,
        "users": users,
        "pending": pending,
        "total_orders": total
    })


# --- 1b. ADMIN USERS LIST ---
@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    """Return list of all non-admin users for User Management page."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT user_id, full_name, email, role, created_at FROM users WHERE role != 'admin' ORDER BY created_at DESC"
        )
        users = cursor.fetchall()
        for u in users:
            if 'created_at' in u and u['created_at']:
                u['created_at'] = str(u['created_at'])
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- 2. ADMIN MENU MANAGEMENT ---
import base64
import os
import uuid


def save_image(base64_str):
    if not base64_str or "base64," not in base64_str:
        return None
    try:
        header, encoded = base64_str.split(",", 1)
        data = base64.b64decode(encoded)
        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(app.static_folder, 'images', filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(data)
        return filename  # Return just filename to store in DB
    except Exception as e:
        print("Image Save Error:", e)
        return None


@app.route('/api/admin/menu/add', methods=['POST'])
def add_menu_item():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        img_filename = save_image(data.get('image'))

        cursor.execute(
            "INSERT INTO menu_items (name, price, category, description, image_url) VALUES (%s, %s, %s, %s, %s)",
            (data['name'], data['price'], data['category'],
             data.get('description', ''), img_filename))
        conn.commit()
        return jsonify({"success": True, "message": "Item Added!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/admin/menu/update/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        img_filename = save_image(
            data.get('image'))  # Will be None if not provided/valid

        if img_filename:
            # Update with new image
            cursor.execute(
                "UPDATE menu_items SET name=%s, price=%s, category=%s, description=%s, image_url=%s WHERE item_id=%s",
                (data['name'], data['price'], data['category'],
                 data.get('description', ''), img_filename, item_id))
        else:
            # Keep old image
            cursor.execute(
                "UPDATE menu_items SET name=%s, price=%s, category=%s, description=%s WHERE item_id=%s",
                (data['name'], data['price'], data['category'],
                 data.get('description', ''), item_id))

        conn.commit()
        return jsonify({"success": True, "message": "Item Updated!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/admin/menu/delete/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM menu_items WHERE item_id=%s", (item_id, ))
        conn.commit()
        return jsonify({"success": True, "message": "Item Deleted!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- 1c. ADMIN BOOKINGS (All reservations) ---
@app.route('/api/admin/bookings', methods=['GET'])
def admin_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT b.booking_id, b.booking_date, b.booking_time, b.guests,
                   b.status, b.table_id, u.full_name, u.email
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            WHERE b.status != 'Deleted'
            ORDER BY b.booking_date DESC, b.booking_time DESC
            """)
        bookings = cursor.fetchall()
        for b in bookings:
            if 'booking_date' in b and b['booking_date']:
                b['booking_date'] = str(b['booking_date'])
            if 'booking_time' in b and b['booking_time']:
                b['booking_time'] = str(b['booking_time'])
        return jsonify({"success": True, "bookings": bookings})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- DELETE BOOKING (Soft Delete) ---
@app.route('/api/admin/booking/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE bookings SET status='Deleted' WHERE booking_id=%s",
            (booking_id, ))
        conn.commit()
        return jsonify({"success": True, "message": "Booking Deleted"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- UPDATE BOOKING STATUS ---
@app.route('/api/admin/booking/update/<int:booking_id>', methods=['POST'])
def update_booking_status(booking_id):
    data = request.json
    new_status = data.get('status')

    if not new_status:
        return jsonify({
            "success": False,
            "message": "No status provided"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE bookings SET status=%s WHERE booking_id=%s",
                       (new_status, booking_id))

        # Notification Logic
        cursor.execute(
            "SELECT u.email FROM bookings b JOIN users u ON b.user_id = u.user_id WHERE b.booking_id = %s",
            (booking_id, ))
        result = cursor.fetchone()
        if result:
            user_email = result[0]
            message = f"Your Table Reservation #{booking_id} status has been updated to: {new_status}"
            cursor.execute(
                "INSERT INTO notifications (user_email, message, type) VALUES (%s, %s, 'Booking')",
                (user_email, message))

        conn.commit()
        return jsonify({"success": True, "message": "Status Updated"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- 2. ADMIN TABLES API (With Reserved By Name) ---
@app.route('/api/admin/tables', methods=['GET'])
def get_tables():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT table_id, table_name, status, reserved_by FROM dining_tables"
        )
        tables = cursor.fetchall()
        return jsonify(tables)
    except Exception as e:
        print(e)
        # Fallback if column missing or error
        return jsonify([])
    finally:
        cursor.close()
        conn.close()

# --- 2b. ADMIN TABLES BY SLOT API ---
@app.route('/api/admin/tables_by_slot', methods=['POST'])
def admin_tables_by_slot():
    data = request.json
    date = data.get('date')
    time = data.get('time')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT table_id, table_name FROM dining_tables")
        tables = cursor.fetchall()
        
        if date and time:
            cursor.execute('''
                SELECT b.table_id, b.status, u.full_name as user_name 
                FROM bookings b
                LEFT JOIN users u ON b.user_id = u.user_id 
                WHERE b.booking_date = %s AND b.booking_time = %s AND b.status != 'Cancelled' AND b.status != 'Deleted'
            ''', (date, time))
            bookings = cursor.fetchall()
            booking_map = {b['table_id']: b for b in bookings}
            
            for t in tables:
                tb_id = t['table_id']
                if tb_id in booking_map:
                    t['status'] = 'Occupied' if booking_map[tb_id]['user_name'] is None else 'Reserved'
                    t['reserved_by'] = booking_map[tb_id]['user_name'] or 'Admin'
                else:
                    t['status'] = 'Available'
                    t['reserved_by'] = ''
        return jsonify(tables)
    except Exception as e:
        print(e)
        return jsonify([])
    finally:
        cursor.close()
        conn.close()


# --- 3. FREE TABLE SLOTS API ---
@app.route('/api/admin/free_table_slot/<int:id>', methods=['POST'])
def free_table_slot(id):
    data = request.json
    date = data.get('date')
    time = data.get('time')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE bookings SET status = 'Cancelled' WHERE table_id = %s AND booking_date = %s AND booking_time = %s",
            (id, date, time))
        conn.commit()
        return jsonify({"success": True, "message": "Table Marked Free!"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --- ADMIN: UPDATE TABLE SLOT STATUS ---
@app.route('/api/admin/update_table_slot/<int:table_id>', methods=['POST'])
def admin_update_table_slot(table_id):
    data = request.json or {}
    status = data.get('status')
    reserved_by = data.get('reserved_by')
    date = data.get('date')
    time = data.get('time')

    if not date or not time:
         return jsonify({"success": False, "message": "Date and Time are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if status == 'Available':
            cursor.execute(
                "UPDATE bookings SET status='Cancelled' WHERE table_id=%s AND booking_date=%s AND booking_time=%s AND status NOT IN ('Cancelled', 'Deleted')",
                (table_id, date, time))
        else:
            # check if exists
            cursor.execute("SELECT booking_id FROM bookings WHERE table_id=%s AND booking_date=%s AND booking_time=%s AND status NOT IN ('Cancelled', 'Deleted')",
                           (table_id, date, time))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO bookings (booking_date, booking_time, guests, status, table_id, user_id) VALUES (%s, %s, 0, 'Confirmed', %s, NULL)",
                    (date, time, table_id))
        conn.commit()
        return jsonify({"success": True, "message": "Updated"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- 4. ADMIN ORDERS (With Transaction Details) ---
@app.route('/api/admin/orders', methods=['GET'])
def admin_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """SELECT o.order_id, o.total_amount, o.status, o.created_at, o.payment_method, 
                      o.transaction_id, o.payment_status, u.full_name, u.phone, u.email, o.delivery_address,
                      o.table_number, o.number_of_guests, o.order_type
               FROM orders o JOIN users u ON o.user_id = u.user_id WHERE o.status != 'Deleted' 
               ORDER BY o.created_at DESC"""
    cursor.execute(query)
    orders = cursor.fetchall()

    for order in orders:
        order['created_at'] = str(
            order['created_at'])  # Fix Date Serialization
        cursor.execute(
            """SELECT mi.name, od.quantity, od.price_at_time FROM order_details od 
                          JOIN menu_items mi ON od.item_id = mi.item_id WHERE od.order_id = %s""",
            (order['order_id'], ))
        order['items'] = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({"success": True, "orders": orders})


# --- UPDATE PAYMENT STATUS ---
@app.route('/api/admin/update_payment/<int:order_id>', methods=['POST'])
def update_payment_status(order_id):
    data = request.json
    new_status = data.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET payment_status=%s WHERE order_id=%s",
                       (new_status, order_id))
        conn.commit()
        return jsonify({"success": True, "message": "Updated"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- 5. UPDATE ORDER STATUS ---
@app.route('/admin/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    # This route handles Form Submit from Old Dashboard AND JSON from New Dashboard
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get status from form or JSON
    if request.is_json:
        data = request.get_json()
        new_status = data.get('status')
    else:
        new_status = request.form.get('status')

    if not new_status:
        return jsonify({
            "success": False,
            "message": "No status provided"
        }), 400

    try:
        # Update Order Status
        cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s",
                       (new_status, order_id))

        # --- Notification Logic ---
        # Fetch User Email to send notification
        cursor.execute(
            "SELECT u.email FROM orders o JOIN users u ON o.user_id = u.user_id WHERE o.order_id = %s",
            (order_id, ))
        result = cursor.fetchone()

        if result:
            user_email = result[0]
            message = f"Your order #{order_id} status has been updated to: {new_status}"
            try:
                cursor.execute(
                    "INSERT INTO notifications (user_email, message, type) VALUES (%s, %s, 'Order')",
                    (user_email, message))
            except Exception as e:
                print(f"Notification error: {e}")  # Log but don't fail

        conn.commit()

        if request.is_json:
            return jsonify({"success": True, "message": "Updated"})
        else:
            return redirect(url_for('admin_dashboard_view'))

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- 6. ADMIN MESSAGES & REPLY ---
@app.route('/api/admin/messages', methods=['GET'])
def admin_messages_api():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT m.message_id, m.subject, m.message, m.admin_reply, u.full_name, m.created_at 
            FROM messages m JOIN users u ON m.user_id = u.user_id 
            ORDER BY m.created_at DESC
        """)
        msgs = cursor.fetchall()
        return jsonify({"messages": msgs})
    except Exception as e:
        return jsonify({"messages": []})
    finally:
        cursor.close()
        conn.close()


@app.route('/api/admin/reply', methods=['POST'])
def admin_reply_api():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        target_type = data.get('target_type', 'user')

        if target_type == 'authority':
            # Reply to a Food Authority warning
            warning_id = data.get('warning_id')
            if not warning_id:
                return jsonify({
                    "success": False,
                    "message": "warning_id required"
                }), 400

            # Check if admin_reply column exists, if not add it
            cursor.execute(
                "SHOW COLUMNS FROM authority_warnings LIKE 'admin_reply'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE authority_warnings ADD COLUMN admin_reply TEXT"
                )

            # Update authority_warnings table with admin_reply
            cursor.execute(
                "UPDATE authority_warnings SET admin_reply = %s WHERE warning_id = %s",
                (data['reply'], warning_id),
            )
        else:
            # Default: reply to normal user message
            # Get user email from message_id
            cursor.execute(
                "SELECT u.email FROM messages m JOIN users u ON m.user_id = u.user_id WHERE m.message_id = %s",
                (data['message_id'], ),
            )
            user_row = cursor.fetchone()

            # Update message with admin reply
            cursor.execute(
                "UPDATE messages SET admin_reply = %s, status = 'Replied' WHERE message_id = %s",
                (data['reply'], data['message_id']),
            )

            # Send notification to user
            if user_row:
                user_email = user_row['email']
                notification_msg = f"Admin replied to your message: {data['reply'][:50]}..."
                try:
                    cursor.execute(
                        "INSERT INTO notifications (user_email, message, type) VALUES (%s, %s, 'Message')",
                        (user_email, notification_msg),
                    )
                except Exception as e:
                    print(f"Notification error: {e}")

        conn.commit()
        return jsonify({"success": True, "message": "Replied!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- 7. ADMIN AUTHENTICATION ---
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    # Hardcoded Credentials as requested
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        session['admin_logged_in'] = True
        return jsonify({"success": True, "message": "Login Successful"})
    return jsonify({"success": False, "message": "Invalid Credentials"}), 401


# --- 8. FETCH NOTIFICATIONS (User Side) ---
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    email = request.args.get('email')
    if not email:
        return jsonify({"notifications": []})

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM notifications WHERE user_email = %s ORDER BY created_at DESC LIMIT 20",
            (email, ))
        notifs = cursor.fetchall()
        # Convert datetime to string
        for notif in notifs:
            if 'created_at' in notif and notif['created_at']:
                notif['created_at'] = str(notif['created_at'])
        return jsonify({"notifications": notifs})
    except Exception as e:
        print(f"Notification error: {e}")
        return jsonify({"notifications": []})
    finally:
        cursor.close()
        conn.close()


# ==========================================
#           REVIEWS & RATINGS API
# ==========================================


# --- SUBMIT REVIEW ---
@app.route('/api/submit_review', methods=['POST'])
def submit_review():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get user_id
        cursor.execute("SELECT user_id FROM users WHERE email = %s",
                       (data['email'], ))
        user_row = cursor.fetchone()
        if not user_row:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        user_id = user_row[0]

        # Get item_id if item_name provided
        item_id = None
        if data.get('item_name'):
            cursor.execute("SELECT item_id FROM menu_items WHERE name = %s",
                           (data['item_name'], ))
            item_row = cursor.fetchone()
            if item_row:
                item_id = item_row[0]

        # Insert Review
        query = """INSERT INTO reviews (user_id, item_id, item_name, rating, comment, order_id) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(
            query, (user_id, item_id, data.get('item_name'), data['rating'],
                    data.get('comment', ''), data.get('order_id')))
        conn.commit()
        return jsonify({"success": True, "message": "Review submitted!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- GET REVIEWS FOR ITEM ---
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    item_name = request.args.get('item_name')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Join with menu_items to get image_url
        # Prefer linking by item_id (r.item_id = mi.item_id)
        if item_name:
            query = """SELECT r.*, u.full_name, mi.image_url 
                       FROM reviews r 
                       JOIN users u ON r.user_id = u.user_id 
                       LEFT JOIN menu_items mi ON r.item_id = mi.item_id
                       WHERE r.item_name = %s 
                       ORDER BY r.created_at DESC"""
            cursor.execute(query, (item_name, ))
        else:
            query = """SELECT r.*, u.full_name, mi.image_url 
                       FROM reviews r 
                       JOIN users u ON r.user_id = u.user_id 
                       LEFT JOIN menu_items mi ON r.item_id = mi.item_id
                       ORDER BY r.created_at DESC LIMIT 50"""
            cursor.execute(query)

        reviews = cursor.fetchall()
        for review in reviews:
            if 'created_at' in review and review['created_at']:
                review['created_at'] = str(review['created_at'])
        return jsonify({"success": True, "reviews": reviews})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Synonym for Admin/Authority use (maps to same function)
@app.route('/api/authority/reviews', methods=['GET'])
def authority_reviews():
    return get_reviews()


# --- DEBUG: FIX DATA ---
@app.route('/api/debug/fix_metadata', methods=['GET'])
def fix_metadata():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fix Reviews
        cursor.execute(
            "UPDATE reviews SET item_name='Legacy Review Item' WHERE item_name IS NULL OR item_name=''"
        )

        # Check if we need to fix images?
        # (Optional: Assign random item_ids if missing, but let's stick to name first)

        conn.commit()
        return jsonify({"success": True, "message": "Fixed legacy data!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        cursor.close()
        conn.close()


# ==========================================
#           FOOD AUTHORITY API ROUTES
# ==========================================


# --- FOOD AUTHORITY LOGIN ---
@app.route('/api/authority/login', methods=['POST'])
def authority_login():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s AND role = 'authority'",
            (data.get('email'), data.get('password')))
        user = cursor.fetchone()
        if user:
            session['authority_logged_in'] = True
            session['authority_email'] = user['email']
            return jsonify({
                "success": True,
                "message": "Login Successful",
                "name": user['full_name']
            })
        return jsonify({
            "success": False,
            "message": "Invalid Credentials"
        }), 401
    finally:
        cursor.close()
        conn.close()


# --- GET MENU PRICES (For Authority) ---
@app.route('/api/authority/prices', methods=['GET'])
def authority_prices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT item_id, name, price, category FROM menu_items ORDER BY price DESC"
        )
        items = cursor.fetchall()
        return jsonify({"success": True, "menu": items})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- SEND WARNING TO ADMIN ---
@app.route('/api/authority/send_warning', methods=['POST'])
def send_warning():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get authority user_id
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s AND role = 'authority'",
            (data.get('authority_email'), ))
        auth_row = cursor.fetchone()
        if not auth_row:
            return jsonify({
                "success": False,
                "message": "Authority not found"
            }), 404
        authority_id = auth_row[0]

        # Get admin user_id
        cursor.execute(
            "SELECT user_id FROM users WHERE role = 'admin' LIMIT 1")
        admin_row = cursor.fetchone()
        admin_id = admin_row[0] if admin_row else None

        # Insert Warning
        query = """INSERT INTO authority_warnings (authority_id, admin_id, warning_message, warning_type) 
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (authority_id, admin_id, data['message'],
                               data.get('type', 'Other')))

        # Also create notification for admin
        cursor.execute("SELECT email FROM users WHERE role = 'admin' LIMIT 1")
        admin_email_row = cursor.fetchone()
        if admin_email_row:
            admin_email = admin_email_row[0]
            cursor.execute(
                "INSERT INTO notifications (user_email, message, type) VALUES (%s, %s, 'Warning')",
                (admin_email, f"⚠️ Food Authority Warning: {data['message']}"))

        conn.commit()
        return jsonify({"success": True, "message": "Warning sent to admin!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- GET ADMIN WARNINGS ---
@app.route('/api/admin/warnings', methods=['GET'])
def get_admin_warnings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """SELECT w.*, u.full_name as authority_name 
                   FROM authority_warnings w 
                   JOIN users u ON w.authority_id = u.user_id 
                   ORDER BY w.created_at DESC"""
        cursor.execute(query)
        warnings = cursor.fetchall()
        for warning in warnings:
            if 'created_at' in warning and warning['created_at']:
                warning['created_at'] = str(warning['created_at'])
        return jsonify({"success": True, "warnings": warnings})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- AUTHORITY: VIEW WARNINGS + ADMIN REPLIES ---
@app.route('/api/authority/warnings', methods=['GET'])
def authority_warnings():
    """
    Food Authority ko un warnings ki list dikhanay ke liye
    jahan admin ne reply bhi kiya ho (ya pending ho).
    """
    email = request.args.get('email')
    if not email:
        return jsonify({"success": False, "warnings": []})

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Find authority user_id from email
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s AND role = 'authority'",
            (email, ))
        auth_row = cursor.fetchone()
        if not auth_row:
            return jsonify({"success": False, "warnings": []})

        authority_id = auth_row['user_id']

        cursor.execute(
            """
            SELECT w.*, a.full_name AS admin_name
            FROM authority_warnings w
            LEFT JOIN users a ON w.admin_id = a.user_id
            WHERE w.authority_id = %s
            ORDER BY w.created_at DESC
            """,
            (authority_id, ),
        )
        warnings = cursor.fetchall()
        for w in warnings:
            if 'created_at' in w and w['created_at']:
                w['created_at'] = str(w['created_at'])
        return jsonify({"success": True, "warnings": warnings})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- VERIFY PAYMENT (Admin) ---
@app.route('/api/admin/verify_payment/<int:order_id>', methods=['POST'])
def verify_payment(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Update payment status
        cursor.execute(
            "UPDATE orders SET payment_status = 'Paid' WHERE order_id = %s",
            (order_id, ))

        # Get user email for notification
        cursor.execute(
            "SELECT u.email FROM orders o JOIN users u ON o.user_id = u.user_id WHERE o.order_id = %s",
            (order_id, ))
        user_email_row = cursor.fetchone()
        if user_email_row:
            user_email = user_email_row[0]
            cursor.execute(
                "INSERT INTO notifications (user_email, message, type) VALUES (%s, %s, 'Order')",
                (user_email, f"✅ Payment verified for Order #{order_id}"))

        conn.commit()
        return jsonify({"success": True, "message": "Payment verified!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ==========================================
#           HTML PAGE ROUTES
# ==========================================


# --- USER ROUTES ---
@app.route('/user/login')
def user_login():
    return render_template('user/login.html')


@app.route('/user/signup')
def user_signup():
    return render_template('user/signup.html')


@app.route('/user/home')
def user_home():
    return render_template('user/home.html')


@app.route('/user/menu')
def user_menu():
    return render_template('user/menu.html')


@app.route('/user/cart')
def user_cart():
    return render_template('user/cart.html')


@app.route('/user/checkout')
def user_checkout():
    return render_template('user/checkout.html')


@app.route('/user/my_orders')
def user_my_orders():
    return render_template('user/my_orders.html')


@app.route('/user/contact')
def user_contact():
    return render_template('user/contact.html')


@app.route('/user/reserve_seat')
def user_reserve_seat():
    return render_template('user/reserve_seat.html')


@app.route('/user/food_detail')
def user_food_detail():
    return render_template('user/food_detail.html')


# --- ADMIN ROUTES ---
@app.route('/admin/login')
def admin_login_page():
    return render_template('admin/login.html')


@app.route('/admin/dashboard')
def admin_dashboard_view():
    return render_template('admin/dashboard.html')


@app.route('/admin/order_management')
def admin_order_management():
    return render_template('admin/order_management.html')


@app.route('/admin/menu_management')
def admin_menu_management():
    return render_template('admin/menu_management.html')


# --- PUBLIC MENU API ---
@app.route('/api/menu', methods=['GET'])
def get_public_menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT item_id, name, price, category, description, image_url, rating, review_count FROM menu_items ORDER BY category, name"
        )
        items = cursor.fetchall()
        return jsonify({"success": True, "menu": items})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- REVIEWS API ---
@app.route('/api/add_review', methods=['POST'])
def add_review():
    data = request.json
    item_id = data.get('item_id')
    user_name = data.get('user_name') or 'Anonymous'
    rating = data.get('rating')
    review_text = data.get('review_text')

    if not item_id or not rating:
        return jsonify({
            "success": False,
            "message": "Item ID and Rating are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Insert Review
        cursor.execute(
            """
            INSERT INTO reviews (item_id, user_name, rating, review_text) 
            VALUES (%s, %s, %s, %s)
        """, (item_id, user_name, rating, review_text))

        # 2. Recalculate Average Rating & Count
        cursor.execute(
            """
            SELECT AVG(rating) as avg_rating, COUNT(*) as count 
            FROM reviews 
            WHERE item_id = %s
        """, (item_id, ))
        result = cursor.fetchone()

        new_rating = float(result['avg_rating']) if result['avg_rating'] else 0
        new_count = result['count']

        # 3. Update menu_items table
        cursor.execute(
            """
            UPDATE menu_items 
            SET rating = %s, review_count = %s 
            WHERE item_id = %s
        """, (new_rating, new_count, item_id))

        conn.commit()
        return jsonify({
            "success": True,
            "message": "Review added!",
            "new_rating": new_rating,
            "new_count": new_count
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/get_reviews/<int:item_id>', methods=['GET'])
def get_reviews_by_id(item_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM reviews WHERE item_id = %s ORDER BY created_at DESC",
            (item_id, ))
        reviews = cursor.fetchall()
        return jsonify({"success": True, "reviews": reviews})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/admin/user_management')
def admin_user_management():
    return render_template('admin/user_management.html')


@app.route('/admin/admin_reviews')
def admin_reviews():
    return render_template('admin/admin_reviews.html')


@app.route('/admin/notifications')
def admin_notifications():
    return render_template('admin/notifications.html')


@app.route('/admin/order_details')
def admin_order_details():
    return render_template('admin/order_details.html')


@app.route('/admin/table_management')
def admin_table_management():
    return render_template('admin/table_management.html')


# --- AUTHORITY ROUTES ---
@app.route('/authority/login')
def authority_login_page():
    return render_template('authority/login.html')


@app.route('/authority/dashboard')
def authority_dashboard():
    return render_template('authority/dashboard.html')


@app.route('/authority/view_reviews')
def authority_view_reviews():
    return render_template('authority/view_reviews.html')


@app.route('/authority/check_prices')
def authority_check_prices():
    return render_template('authority/check_prices.html')


@app.route('/authority/send_notification')
def authority_send_notification():
    return render_template('authority/send_notification.html')


# --- DELETE ORDER (Soft Delete) ---
@app.route('/api/admin/order/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET status='Deleted' WHERE order_id=%s",
                       (order_id, ))
        conn.commit()
        return jsonify({"success": True, "message": "Order Deleted"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    # Suppress Flask Development Server Warning
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    def open_browser():
        import webbrowser
        try:
            webbrowser.open("http://127.0.0.1:5000")
        except Exception:
            pass

    # SIRF IS HISSE KO CHANGE KAREIN:
    # Werkzeug check karta hai ke kya yeh reloader process hai
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        from threading import Timer
        Timer(1.5, open_browser).start()

    app.run(debug=True, port=5000)
