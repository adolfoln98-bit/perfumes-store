from db import get_session
from repositories import perfumes_repository
from sqlalchemy.exc import IntegrityError
from psycopg.errors import ForeignKeyViolation
from exceptions import perfumes
from exceptions import marcas


def crear_perfume(nombre, volumen_ml, marca_id):
    with get_session() as session:
        
        try:
           perfume = perfumes_repository.crear_perfume(session, nombre, volumen_ml, marca_id)
           session.flush()
           id_perfume = perfume.id
           session.commit()
           
        except IntegrityError as error:
            session.rollback()
            
            if isinstance(error.orig, ForeignKeyViolation):
                raise marcas.MarcaNoEncontradaError("La marca no existe")
            
            raise
            
    return id_perfume

def obtener_perfumes():
    with get_session() as session:
        perfumes = perfumes_repository.obtener_perfumes(session)
    
    return perfumes

def obtener_perfume_por_id(id_perfume):
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
    if perfume is None:
        raise perfumes.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
    return perfume

def actualizar_perfume(id_perfume, nuevo_nombre, nuevo_volumen, nueva_marca_id):
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
        if perfume is None:
            raise perfumes.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
        try:
            perfumes_repository.actualizar_perfume(
                perfume,
                nuevo_nombre,
                nuevo_volumen,
                nueva_marca_id
                )
            session.flush()
            session.commit()
        
        except IntegrityError as error:
            session.rollback()
            
            if isinstance(error.orig, ForeignKeyViolation):
                raise marcas.MarcaNoEncontradaError("La marca no existe")
            raise
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        resultado = (perfume.nombre,
                     perfume.volumen_ml,
                     perfume.marca.nombre if perfume.marca else None)
        
    return resultado

def eliminar_perfume(id_perfume):
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
        if perfume is None:
            raise perfumes.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
        perfumes_repository.eliminar_perfume(session, perfume)
        
        session.flush()    
        session.commit()
    return "El perfume ha sido borrado correctamente"
        