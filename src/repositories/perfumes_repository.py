from db import get_connection
from psycopg.rows import dict_row
from psycopg.errors import ForeignKeyViolation

class MarcaNoEncontradaError(Exception):
    pass

def crear_perfume(perfume_nombre, volumen_ml, marca_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO perfumes(nombre, volumen_ml, marca_id)
                VALUES (%s, %s, %s)
                RETURNING id
                """, (perfume_nombre, volumen_ml, marca_id))
                id_perfume = cursor.fetchone()[0]
                conn.commit()
    except ForeignKeyViolation:
        raise MarcaNoEncontradaError(f'No existe ninguna marca con el id {marca_id}')
    
    return id_perfume

def obtener_perfumes():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
            SELECT perfumes.id,
            perfumes.nombre AS perfume,
            marcas.nombre as marca, 
            perfumes.volumen_ml 
            FROM perfumes
            INNER JOIN marcas
            ON perfumes.marca_id=marcas.id
            """)
            perfumes = cursor.fetchall()
    return perfumes