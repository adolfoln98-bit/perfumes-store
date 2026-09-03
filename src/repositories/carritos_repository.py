from models import Carrito, LineaCarrito, Perfume
from sqlalchemy import select
from sqlalchemy.orm import joinedload

def obtener_carrito_por_usuario(session, id_usuario):
    
    consulta = select(Carrito).where(Carrito.usuario_id == id_usuario)
    
    resultado = session.execute(consulta)
    
    return resultado.scalar_one_or_none()

def crear_carrito(session, id_usuario):
    
    carrito = Carrito(
        usuario_id = id_usuario
    )
    
    session.add(carrito)
    
    return carrito

def obtener_carrito_por_id(session, id_carrito):
    return session.get(Carrito, id_carrito)

def obtener_carrito_completo_por_id(session, id_carrito):
    consulta_carrito = select(Carrito).options(
        joinedload(Carrito.lineas_carrito).
        joinedload(LineaCarrito.perfume).
        joinedload(Perfume.marca)
    ).where(Carrito.id == id_carrito)
    
    resultado = session.execute(consulta_carrito)
    
    return resultado.unique().scalar_one_or_none()