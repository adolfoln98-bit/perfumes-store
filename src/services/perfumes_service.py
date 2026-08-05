from db import get_session
from repositories import perfumes_repository
from sqlalchemy.exc import IntegrityError
from psycopg.errors import ForeignKeyViolation
from exceptions import perfumes, marcas

def validar_precio(precio):
    if precio <= 0:
        raise perfumes.PrecioIncorrectoError("El precio introducido no es valido.")

def validar_stock(stock):
    if stock < 0:
        raise perfumes.StockIncorrectoError("El stock introducido no es valido.")

def validar_cantidad_stock(cantidad_stock):
    if cantidad_stock <= 0:
        raise perfumes.CantidadStockIncorrectaError("El stock introducido no es valido.")

def crear_perfume(nombre, volumen_ml, marca_id, precio, stock=0):
    
    validar_precio(precio)
    validar_stock(stock)
    
    with get_session() as session:
        
        try:
           perfume = perfumes_repository.crear_perfume(session, nombre, volumen_ml, marca_id, precio, stock)
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

def actualizar_perfume(id_perfume, nuevo_nombre, nuevo_volumen, nueva_marca_id, nuevo_precio, nuevo_stock):
    
    validar_precio(nuevo_precio)
    validar_stock(nuevo_stock)
    
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
        if perfume is None:
            raise perfumes.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
        try:
            perfumes_repository.actualizar_perfume(
                perfume,
                nuevo_nombre,
                nuevo_volumen,
                nueva_marca_id,
                nuevo_precio,
                nuevo_stock
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

def reponer_stock(id_perfume, cantidad):
    
    validar_cantidad_stock(cantidad)
    
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
                
        if perfume is None:
            raise perfumes.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
        perfumes_repository.reponer_stock(
            perfume,
            cantidad
        )
        session.flush()
        nuevo_stock = perfume.stock
        session.commit()
                    
                
        return nuevo_stock