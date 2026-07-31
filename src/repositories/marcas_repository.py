from sqlalchemy import select
from models import Marca

def crear_marca(session, nombre):
     
    marca = Marca(nombre=nombre)
    session.add(marca)

    return marca

def obtener_marcas(session):
    
    consulta_marcas = select(Marca)
    resultado = session.execute(consulta_marcas)
    marcas = resultado.scalars().all()
            
    return marcas

def obtener_marca_por_id(session, id_marca):
    return session.get(Marca, id_marca)

def actualizar_marca(marca, nuevo_nombre):
    marca.nombre = nuevo_nombre
    

def eliminar_marca(session, marca):
    session.delete(marca)
    