from models import Perfume
from sqlalchemy import select
from sqlalchemy.orm import joinedload


def crear_perfume(session, nombre, volumen_ml, marca_id):
    perfume = Perfume(
        nombre=nombre,
        volumen_ml=volumen_ml,
        marca_id=marca_id
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

def actualizar_perfume(perfume, nuevo_nombre, nuevo_volumen, nueva_marca_id):
    perfume.nombre = nuevo_nombre
    perfume.volumen_ml = nuevo_volumen
    perfume.marca_id = nueva_marca_id

def eliminar_perfume(session, perfume):
    session.delete(perfume)