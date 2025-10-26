# api/actions.py

from flask import jsonify, request
from datetime import datetime
from db import get_db_connection, query_db


def get_inventory():
    product_id = request.args.get('product_id')
    sku = request.args.get('sku')
    warehouse = request.args.get('warehouse')

    query = "SELECT * FROM inventory WHERE 1=1"
    params = []

    if product_id:
        query += " AND product_id=%s"
        params.append(product_id)
    if sku:
        query += " AND sku=%s"
        params.append(sku)
    if warehouse:
        query += " AND warehouse=%s"
        params.append(warehouse)

    result = query_db(query, tuple(params), fetch=True)
    return jsonify({"items": result})


def reserve_stock():
    data = request.get_json()
    order_id = data['order_id']
    items = data['items']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        for item in items:
            cursor.execute("""
                SELECT on_hand, reserved FROM inventory
                WHERE product_id=%s AND warehouse=%s
            """, (item['product_id'], item['warehouse']))
            row = cursor.fetchone()
            if not row or (row['on_hand'] - row['reserved']) < item['quantity']:
                return jsonify({"error": "Insufficient stock", "product_id": item['product_id']}), 400

        for item in items:
            cursor.execute("""
                UPDATE inventory 
                SET reserved = reserved + %s, updated_at=%s
                WHERE product_id=%s AND warehouse=%s
            """, (item['quantity'], datetime.now(), item['product_id'], item['warehouse']))

            cursor.execute("""
                INSERT INTO inventory_movements
                (product_id, sku, warehouse, movement_type, quantity, reference, created_at)
                VALUES (%s,%s,%s,'RESERVE',%s,%s,%s)
            """, (item['product_id'], item['sku'], item['warehouse'], item['quantity'], order_id, datetime.now()))

        conn.commit()
        return jsonify({"status": "success", "message": f"Reserved {len(items)} items"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def release_stock():
    data = request.get_json()
    order_id = data['order_id']
    items = data['items']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        for item in items:
            cursor.execute("""
                UPDATE inventory 
                SET reserved = reserved - %s, updated_at=%s
                WHERE product_id=%s AND warehouse=%s
            """, (item['quantity'], datetime.now(), item['product_id'], item['warehouse']))

            cursor.execute("""
                INSERT INTO inventory_movements
                (product_id, sku, warehouse, movement_type, quantity, reference, created_at)
                VALUES (%s,%s,%s,'RELEASE',%s,%s,%s)
            """, (item['product_id'], item['sku'], item['warehouse'], item['quantity'], order_id, datetime.now()))

        conn.commit()
        return jsonify({"status": "success", "message": f"Released {len(items)} items"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def ship_stock():
    data = request.get_json()
    order_id = data['order_id']
    items = data['items']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        for item in items:
            cursor.execute("""
                UPDATE inventory
                SET on_hand = on_hand - %s,
                    reserved = reserved - %s,
                    updated_at=%s
                WHERE product_id=%s AND warehouse=%s
            """, (item['quantity'], item['quantity'], datetime.now(), item['product_id'], item['warehouse']))

            cursor.execute("""
                INSERT INTO inventory_movements
                (product_id, sku, warehouse, movement_type, quantity, reference, created_at)
                VALUES (%s,%s,%s,'SHIP',%s,%s,%s)
            """, (item['product_id'], item['sku'], item['warehouse'], item['quantity'], order_id, datetime.now()))

        conn.commit()
        return jsonify({"status": "success", "message": f"Shipped {len(items)} items"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def low_stock():
    threshold = int(request.args.get('threshold', 5))
    result = query_db("""
        SELECT *, (on_hand - reserved) AS available 
        FROM inventory
        WHERE (on_hand - reserved) < %s
    """, (threshold,), fetch=True)
    return jsonify(result)
