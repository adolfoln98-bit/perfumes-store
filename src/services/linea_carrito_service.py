from db import get_session
from repositories import(
    linea_carrito_repository,
    perfumes_repository,
    carritos_repository
    )
from exceptions import linea_carrito as linea_carrito_exception
from exceptions import perfumes as perfumes_exception
from exceptions import usuarios as usuarios_exception
from exceptions import carrito as carrito_exception
from services import carritos_service

from sqlalchemy.exc import IntegrityError
from psycopg.errors import ForeignKeyViolation

def obtener_linea_carrito(carrito_id, perfume_id):
    
    with get_session() as session:
        linea_carrito = linea_carrito_repository.obtener_linea_carrito(session, carrito_id, perfume_id)
        
    return linea_carrito

def agregar_perfume_al_carrito(id_usuario, id_perfume, cantidad):
    
    if cantidad <= 0:
        raise linea_carrito_exception.CantidadInvalidaError("La cantidad es incorrecta")
    
    with get_session() as session:
        try:
            carrito = carritos_service._crear_o_obtener_carrito(session, id_usuario) 
            session.flush()
        
            perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
            if not perfume:
                raise perfumes_exception.PerfumeNoEncontradoError("No se encontro el perfume")
        
            linea_carrito = linea_carrito_repository.obtener_linea_carrito(session, carrito.id, perfume.id)
        
            if linea_carrito:
                cantidad_total = linea_carrito.cantidad + cantidad
            else:
                cantidad_total = cantidad
        
            if cantidad_total > perfume.stock:
                raise linea_carrito_exception.StockInsuficienteError("No hay stock suficiente")            
            
            if linea_carrito:
                linea_carrito_repository.aumentar_cantidad(linea_carrito, cantidad)
            else:
                linea_carrito = linea_carrito_repository.crear_linea_carrito(session, carrito.id, perfume.id, cantidad)

            session.flush()
            id_carrito = carrito.id
            session.commit()
              
        except IntegrityError as error:
            session.rollback()
            
            if isinstance(error.orig, ForeignKeyViolation):
                raise usuarios_exception.UsuarioNoEncontradoError("No se encontro el usuario")
            
            raise
        
        except(
            perfumes_exception.PerfumeNoEncontradoError,
            linea_carrito_exception.StockInsuficienteError
        ):
            session.rollback()
            raise
    
    with get_session() as session:
        carrito_completo = carritos_repository.obtener_carrito_completo_por_id(session, id_carrito)
        
    return carrito_completo

def modificar_cantidad(id_usuario, id_perfume, nueva_cantidad):
    
    if nueva_cantidad <= 0:
        raise linea_carrito_exception.CantidadInvalidaError("La nueva cantidad es incorrecta")
    
    with get_session() as session:
        try:
            carrito = carritos_service._obtener_carrito_por_usuario(session, id_usuario) 
        
            perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
            if not perfume:
                raise perfumes_exception.PerfumeNoEncontradoError("No se encontro el perfume")
            
            linea_carrito = linea_carrito_repository.obtener_linea_carrito(session, carrito.id, id_perfume)
            if not linea_carrito:
                raise linea_carrito_exception.LineaNoEncontradaError("No se encontro la linea del carrito")
            
            if perfume.stock < nueva_cantidad:
                raise linea_carrito_exception.StockInsuficienteError("No hay stock suficiente")
            
            linea_carrito_repository.modificar_cantidad(linea_carrito, nueva_cantidad)
            
            session.flush()
            id_carrito = carrito.id
            session.commit()
        except(
            carrito_exception.CarritoNoEncontradoError,
            perfumes_exception.PerfumeNoEncontradoError,
            linea_carrito_exception.LineaNoEncontradaError,
            linea_carrito_exception.StockInsuficienteError
        ):
            session.rollback()
            raise
    with get_session() as session:
        carrito_actualizado = carritos_repository.obtener_carrito_completo_por_id(session, id_carrito) 
    
    return carrito_actualizado

def eliminar_perfume_del_carrito(id_usuario, id_perfume):
    
    with get_session() as session:
        
        try:
            carrito = carritos_service._obtener_carrito_por_usuario(session, id_usuario)
            
            linea_carrito = linea_carrito_repository.obtener_linea_carrito(session, carrito.id, id_perfume)
            if not linea_carrito:
                raise linea_carrito_exception.LineaNoEncontradaError("No se encontro la linea del carrito")
            
            linea_carrito_repository.eliminar_linea_carrito(session, linea_carrito)
            session.flush()
            id_carrito = carrito.id
            session.commit()
        except (
            carrito_exception.CarritoNoEncontradoError,
            linea_carrito_exception.LineaNoEncontradaError
        ):
            session.rollback()
            raise
    with get_session() as session:
        carrito_actualizado = carritos_repository.obtener_carrito_completo_por_id(session, id_carrito) 
    
    return carrito_actualizado 