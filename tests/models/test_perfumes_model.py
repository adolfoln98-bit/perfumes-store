from models import Perfume
from decimal import Decimal

from sqlalchemy import select

from services import(
    marcas_service,
    perfumes_service
)

def crear_perfume(precio, descuento):
    perfume = Perfume(    
    precio = Decimal(precio),
    descuento = descuento
    )
    return perfume


def obtener_objeto_marca(override_marca_session, nombre_marca):
    id_marca = marcas_service.crear_marca(nombre_marca)
    return marcas_service.obtener_marca_por_id(id_marca)

def obtener_perfume_precio(override_perfume_session, id_marca, precio):
    datos_perfume = {
            "nombre": "perfume",
            "volumen_ml": 50,
            "marca_id": id_marca,
            "precio": precio,
            "stock": 10
        }
    perfume_id = perfumes_service.crear_perfume(
            datos_perfume["nombre"],
            datos_perfume["volumen_ml"],
            datos_perfume["marca_id"],
            datos_perfume["precio"],
            datos_perfume["stock"]
            )
    
    return override_perfume_session.get(Perfume, perfume_id)



def test_perfume_sin_descuento():
    perfume = crear_perfume(Decimal("75.00"), None)
    
    assert perfume.precio_final == Decimal("75.00")


def test_perfume_con_descuento():
    perfume = crear_perfume(Decimal("75.00"), 20)
    
    # el 20% de 75 es 15 de modo que el precio final deberia ser 60 (75-15)
    assert perfume.precio_final == Decimal("60.00")


def test_perfume_con_descuento_redondeo_monetario():
    perfume = crear_perfume(Decimal("99.99"), 17)
    
    #el 17% de 99.99 es 16.9983 de modo que el precio descontado es 82.9917 por lo que el precio final debe ser 82.99
    assert perfume.precio_final == Decimal("82.99")


def test_consulta_sql_perfume_con_descuento(
    override_marca_session,
    override_perfume_session
):
    marca = obtener_objeto_marca(override_marca_session, "Prada")
    
    perfume = obtener_perfume_precio(override_perfume_session, marca.id, Decimal("100.00"))
    obtener_perfume_precio(override_perfume_session, marca.id, Decimal("100.00"))
    
    perfume.descuento = 25
    override_perfume_session.commit()
    
    consulta = select(Perfume).where(
        Perfume.precio_final == Decimal("75.00")
    )
    resultado = override_perfume_session.execute(consulta).scalars().all()
    
    assert len(resultado) == 1
    
    perfume_consulta = resultado[0]
    assert perfume_consulta.id == perfume.id