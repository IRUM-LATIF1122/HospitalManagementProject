from database.connection import get_connection

conn = get_connection()
if conn:
    print("Connection is ready to use.")
    conn.close()
