from sqlalchemy import select
from models import Marca

def crear_marca(session, nombre_marca):
     
    marca = Marca(nombre=nombre_marca)
    session.add(marca)

    return marca

def obtener_marcas(session):
    
    consulta_marcas = select(Marca)
    resultado = session.execute(consulta_marcas)
    marcas = resultado.scalars().all()
            
    return marcas

