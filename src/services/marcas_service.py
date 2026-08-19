from db import get_session
from repositories import marcas_repository
from sqlalchemy.exc import IntegrityError
from exceptions import marcas


def crear_marca(nombre):
    with get_session() as session:
        try:
           marca = marcas_repository.crear_marca(session, nombre)
           session.flush()
           id_marca = marca.id
           session.commit()
        except IntegrityError:
            session.rollback()
            raise marcas.MarcaDuplicadaError(f"La marca {nombre} ya habia sido añadida previamente")
    return id_marca

def obtener_marcas():
    with get_session() as session:
        marcas = marcas_repository.obtener_marcas(session)
    
    return marcas

def obtener_marca_por_id(id_marca):
    
    with get_session() as session:
        marca = marcas_repository.obtener_marca_por_id(session, id_marca)
    
    if marca is None:
        raise marcas.MarcaNoEncontradaError(f"No se ha encontrado ninguna marca con el id: {id_marca}")
    
    return marca

def actualizar_marca(id_marca, nuevo_nombre):
    
    with get_session() as session:
        marca = marcas_repository.obtener_marca_por_id(session, id_marca)
        if marca is None:
            raise marcas.MarcaNoEncontradaError(f"No se ha encontrado ninguna marca con el id: {id_marca}")
        try:
            marcas_repository.actualizar_marca(
                marca, 
                nuevo_nombre)
            
            session.flush()
            session.commit()
            
        except IntegrityError:
            session.rollback()
            raise marcas.MarcaDuplicadaError(f"La marca {nuevo_nombre} ya habia sido añadida previamente")
            
        with get_session() as session:
            marca = marcas_repository.obtener_marca_por_id(session, id_marca)
        
        return marca

def eliminar_marca(id_marca):
    
    with get_session() as session:
        marca = marcas_repository.obtener_marca_por_id(session, id_marca)
        if marca is None:
            raise marcas.MarcaNoEncontradaError(f"No se ha encontrado ninguna marca con el id: {id_marca}")
        
        marcas_repository.eliminar_marca(
            session, 
            marca)

        session.flush()
        session.commit()

    return "La marca ha sido borrada correctamente"
        