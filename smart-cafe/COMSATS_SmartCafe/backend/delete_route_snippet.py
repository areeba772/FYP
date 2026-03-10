
# --- DELETE ORDER (Soft Delete) ---
@app.route('/api/admin/order/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET status='Deleted' WHERE order_id=%s", (order_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Order Deleted"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
