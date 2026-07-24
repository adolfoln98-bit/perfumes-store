from db import get_session
from repositories import marcas_repository
from sqlalchemy.exc import IntegrityError
from exceptions import marcas


def crear_marca(nombre_marca):
    with get_session() as session:
        try:
           marca = marcas_repository.crear_marca(session, nombre_marca)
           session.flush()
           id_marca = marca.id
           session.commit()
        except IntegrityError:
            session.rollback()
            raise marcas.MarcaDuplicadaError(f"La marca {nombre_marca} ya habia sido añadida previamente")
    return id_marca

def obtener_marcas():
    with get_session() as session:
        marcas = marcas_repository.obtener_marcas(session)
    
    return marcas