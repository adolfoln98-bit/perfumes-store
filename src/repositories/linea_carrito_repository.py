from models import LineaCarrito

from sqlalchemy import select


def obtener_linea_carrito(session, carrito_id, perfume_id):
    
    consulta = select(LineaCarrito).where(
            LineaCarrito.carrito_id == carrito_id,
            LineaCarrito.perfume_id == perfume_id)
    resultado = session.execute(consulta)
    
    return resultado.scalar_one_or_none()

def crear_linea_carrito(session, carrito_id, perfume_id, cantidad):
    linea_carrito = LineaCarrito(
        carrito_id = carrito_id,
        perfume_id = perfume_id,
        cantidad = cantidad
    )
    
    session.add(linea_carrito)
    
    return linea_carrito

def aumentar_cantidad(linea_carrito, cantidad):
    linea_carrito.cantidad += cantidad

