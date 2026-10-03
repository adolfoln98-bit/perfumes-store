from models import Perfume
from decimal import Decimal

def crear_perfume(precio, descuento):
    perfume = Perfume(    
    precio = Decimal(precio),
    descuento = descuento
    )
    return perfume


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