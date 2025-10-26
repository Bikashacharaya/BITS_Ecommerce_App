from db import get_db_connection

def get_next_product_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(product_id) FROM products")
    last_id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return 1 if last_id is None else last_id + 1


def build_get_products_query(name=None, category=None, price=None, is_active=None):
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE %s"
        params.append(f"%{name}%")
    if category:
        query += " AND category LIKE %s"
        params.append(f"%{category}%")
    if price is not None:
        query += " AND price = %s"
        params.append(price)
    if is_active is not None:
        query += " AND is_active = %s"
        params.append(is_active)

    return query, params


def create_product(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    new_id = get_next_product_id()

    cursor.execute(
        "INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES (%s, %s, %s, %s, %s, %s)",
        (new_id, data['sku'], data['name'], data['category'], data['price'], data.get('is_active', True))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return new_id


def get_all_products(filters):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query, params = build_get_products_query(**filters)
    cursor.execute(query, params)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products


def get_product_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return product


def update_product(product_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET sku=%s, name=%s, category=%s, price=%s, is_active=%s WHERE product_id=%s",
        (data['sku'], data['name'], data['category'], data['price'], data.get('is_active', True), product_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.rowcount  # 0 if not found, >0 if updated


def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.rowcount
