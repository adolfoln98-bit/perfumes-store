from db import get_connection

with get_connection() as conn:

    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT CURRENT_TIMESTAMP;
        """)

        respuesta = cursor.fetchone()
        print(respuesta[0])