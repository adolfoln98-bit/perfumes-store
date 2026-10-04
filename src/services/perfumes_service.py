from db import get_session
from repositories import perfumes_repository
from sqlalchemy.exc import IntegrityError
from psycopg.errors import ForeignKeyViolation
from exceptions import perfumes as perfumes_exception
from exceptions import marcas as marcas_exception

def validar_precio(precio):
    if precio <= 0:
        raise perfumes_exception.PrecioIncorrectoError("El precio introducido no es valido.")

def validar_stock(stock):
    if stock < 0:
        raise perfumes_exception.StockIncorrectoError("El stock introducido no es valido.")

def validar_cantidad_stock(cantidad_stock):
    if cantidad_stock < 0:
        raise perfumes_exception.CantidadStockIncorrectaError("El stock introducido no es valido.")

def validar_volumen_ml(volumen_ml):
    if volumen_ml <= 0:
        raise perfumes_exception.VolumenInvalidoError("El volumen es invalido")
        
def validar_marca_id(marca_id):
    if marca_id <= 0:
        raise marcas_exception.MarcaIdInvalidaError("El id de la marca es incorrecta")

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
                raise marcas_exception.MarcaNoEncontradaError("La marca no existe")
            
            raise
            
    return id_perfume

def obtener_perfumes(nombre_marca=None, precio_min=None, precio_max=None, ordenar_por="marca", direccion="asc", en_oferta=None):
    
    if precio_min is not None and precio_max is not None and precio_max < precio_min:
        raise perfumes_exception.FiltroPrecioInvalidoError("El precio minimo debe ser menor que el maximo")
    
    ordenar_por_valido = ["marca", "nombre", "precio"]
    direccion_valida = ["asc", "desc"]
    
    if ordenar_por.lower() not in ordenar_por_valido:
        raise perfumes_exception.CriterioDeOrdenacionInvalidaError("Criterio de ordenación inválido")
    
    if direccion.lower() not in direccion_valida:
        raise perfumes_exception.DireccionDeOrdenacionInvalidaError("Dirección de ordenación inválida")            
    
    with get_session() as session:
        perfumes = perfumes_repository.obtener_perfumes(
            session,
            nombre_marca,
            precio_min,
            precio_max,
            ordenar_por.lower(),
            direccion.lower(),
            en_oferta
        )
    
    return perfumes

def obtener_perfume_por_id(id_perfume):
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
    if perfume is None:
        raise perfumes_exception.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
    return perfume

def actualizar_perfume(id_perfume, **cambios):
    
    if not cambios:
        raise perfumes_exception.CampoActualizacionInvalidoError("No hay cambios a realizar")
    
    campos_validos = {
        "nombre",
        "volumen_ml",
        "marca_id",
        "precio"
    }
    campos_invalidos = set(cambios.keys()) - campos_validos
    
    if campos_invalidos:
        raise perfumes_exception.CampoActualizacionInvalidoError(f"Se ha intentado modificar mediante la actualización general un campo que no está permitido: {campos_invalidos}")
    
    if "precio" in cambios:
            validar_precio(cambios["precio"])
        
    if "volumen_ml" in cambios:
        validar_volumen_ml(cambios["volumen_ml"])
           
    if "marca_id" in cambios:
        validar_marca_id(cambios["marca_id"])
    
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
        if perfume is None:
            raise perfumes_exception.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
        try:
            perfumes_repository.actualizar_perfume(
                perfume,
                **cambios
                )
            session.flush()
            session.commit()
        
        except IntegrityError as error:
            session.rollback()
            
            if isinstance(error.orig, ForeignKeyViolation):
                raise marcas_exception.MarcaNoEncontradaError("La marca no existe")
            raise
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
    return perfume

def eliminar_perfume(id_perfume):
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
        if perfume is None:
            raise perfumes_exception.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
        perfumes_repository.eliminar_perfume(session, perfume)
        
        session.flush()    
        session.commit()
    return "El perfume ha sido borrado correctamente"

def reponer_stock(id_perfume, cantidad):
    
    validar_cantidad_stock(cantidad)
    
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
                
        if perfume is None:
            raise perfumes_exception.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
        perfumes_repository.reponer_stock(
            perfume,
            cantidad
        )
        session.flush()
        session.commit()
        
    with get_session() as session:
        perfume_actualizado = perfumes_repository.obtener_perfume_por_id(session, id_perfume)            
                
    return perfume_actualizado


def administrar_descuento(id_perfume, descuento):
    
    if descuento is not None and (descuento >= 100 or descuento <= 0):
        raise perfumes_exception.DescuentoInvalidoError("El descuento debe ser mayor de 0 y menor de 100")
    
    with get_session() as session:
        perfume = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
        
        if perfume is None:
            raise perfumes_exception.PerfumeNoEncontradoError(f"No se ha encontrado el perfume con el id: {id_perfume}")
        
        perfumes_repository.actualizar_descuento(
            perfume,
            descuento
        )
        session.flush()
        session.commit()
    
    with get_session() as session:
        perfume_actualizado = perfumes_repository.obtener_perfume_por_id(session, id_perfume)
    
    return perfume_actualizado