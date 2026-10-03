from models import Perfume, Marca
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


def obtener_perfumes(session, nombre_marca=None, precio_min=None, precio_max=None, ordenar_por="marca", direccion= "asc"):
    consulta_perfumes = select(Perfume)
    
    if nombre_marca is not None or ordenar_por == "marca":
        consulta_perfumes = consulta_perfumes.join(Perfume.marca)
        
        if nombre_marca is not None:
            consulta_perfumes = consulta_perfumes.where(Marca.nombre.ilike(f"%{nombre_marca}%"))
            
    if precio_min is not None:
        consulta_perfumes = consulta_perfumes.where(Perfume.precio >= precio_min)
    
    if precio_max is not None:
        consulta_perfumes = consulta_perfumes.where(Perfume.precio <= precio_max)
    
    
    if ordenar_por == "marca":
        columnas = [Marca.nombre, Perfume.nombre]
                  
    elif ordenar_por == "nombre":
        columnas = [Perfume.nombre]
            
    elif ordenar_por == "precio":
        columnas = [Perfume.precio]
    
    orden_columnas = []
    if direccion == "asc":
        for columna in columnas:
            orden_columnas.append(columna.asc())
    else:
        for columna in columnas:
            orden_columnas.append(columna.desc())
        
    consulta_perfumes = consulta_perfumes.options(
        joinedload(Perfume.marca)
        )
    resultado = session.execute(consulta_perfumes.order_by(*orden_columnas))
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

    
def descontar_stock(perfume, cantidad):
    perfume.stock-= cantidad


def actualizar_descuento(perfume, descuento):
    perfume.descuento = descuento