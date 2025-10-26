# db.py

import mysql.connector
import config


def get_db_connection():
    """Return a new MySQL connection"""
    conn = mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE
    )
    return conn


def query_db(query, args=(), fetch=False):
    """Run a query and optionally fetch results"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, args)

    if fetch:
        result = cursor.fetchall()
    else:
        conn.commit()
        result = cursor.rowcount

    cursor.close()
    conn.close()
    return result
