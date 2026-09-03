from db import get_session
from repositories import carritos_repository
from sqlalchemy.exc import IntegrityError
from psycopg.errors import ForeignKeyViolation
from exceptions import usuarios as usuarios_exception

import models

def _crear_o_obtener_carrito(session, id_usuario):
    carrito = carritos_repository.obtener_carrito_por_usuario(session, id_usuario)
            
    if not carrito:    
        carrito = carritos_repository.crear_carrito(session, id_usuario)
        
    return carrito


def crear_o_obtener_carrito(id_usuario):
    
    with get_session() as session:
        try:
            carrito = _crear_o_obtener_carrito(session, id_usuario)
            session.flush()
            id_carrito = carrito.id
            session.commit()
        except IntegrityError as error:
            session.rollback()
                        
            if isinstance(error.orig, ForeignKeyViolation):
                raise usuarios_exception.UsuarioNoEncontradoError("El usuario no existe")
            raise
    with get_session() as session:
        carrito = carritos_repository.obtener_carrito_por_id(session, id_carrito)
        
    return carrito
