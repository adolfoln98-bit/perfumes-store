from models import Perfume
from sqlalchemy import select
from sqlalchemy.orm import joinedload


def crear_perfume(session, nombre, volumen_ml, marca_id, precio, stock):
    perfume = Perfume(
        nombre=nombre,
        volumen_ml=volumen_ml,
        marca_id=marca_id,
        precio=precio,
        stock=stock
        )
    session.add(perfume)
    
    return perfume

def obtener_perfumes(session):
    consulta_perfumes = select(Perfume).options(
        joinedload(Perfume.marca)
        )
    
    resultado = session.execute(consulta_perfumes)
    perfumes = resultado.scalars().all()
    
    return perfumes

def obtener_perfume_por_id(session, id_perfume):
    
    consulta_perfumes = (
        select(Perfume)
        .options(joinedload(Perfume.marca))
        .where(Perfume.id == id_perfume)
    )
    
    resultado = session.execute(consulta_perfumes)
    
    return resultado.scalar_one_or_none()

def actualizar_perfume(perfume, **cambios):
    
    for atributo, valor in cambios.items():
        setattr(perfume, atributo, valor)

def eliminar_perfume(session, perfume):
    session.delete(perfume)

def reponer_stock(perfume, cantidad):
    perfume.stock += cantidad