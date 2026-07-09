from db import get_connection
from psycopg.rows import dict_row
from psycopg.errors import UniqueViolation

class MarcaDuplicadaError(Exception):
    pass

def crear_marca(nombre_marca):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO marcas(nombre)
                VALUES (%s)
                RETURNING id
                """, (nombre_marca,))
                id_marca = cursor.fetchone()[0]
                conn.commit()
    except UniqueViolation:
        raise MarcaDuplicadaError(f'La marca {nombre_marca} ya existe')        
    return id_marca

def obtener_marcas():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
            SELECT id, nombre
            FROM marcas
            """)
            marcas = cursor.fetchall()
    return marcas

