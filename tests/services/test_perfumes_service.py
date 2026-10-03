import models
import pytest
from decimal import Decimal

from services import (
    marcas_service,
    perfumes_service
)
from exceptions import perfumes as perfumes_exception

def obtener_objeto_marca(override_marca_session, nombre_marca):
    id_marca = marcas_service.crear_marca(nombre_marca)
    
    return override_marca_session.get(models.Marca, id_marca)

def obtener_perfume(override_perfume_session, id_marca, stock):
    datos_perfume = {
            "nombre": "perfume",
            "volumen_ml": 50,
            "marca_id": id_marca,
            "precio": 50,
            "stock": stock
        }
    perfume_id = perfumes_service.crear_perfume(
            datos_perfume["nombre"],
            datos_perfume["volumen_ml"],
            datos_perfume["marca_id"],
            datos_perfume["precio"],
            datos_perfume["stock"]
            )
    
    return override_perfume_session.get(models.Perfume, perfume_id)

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
    
    return override_perfume_session.get(models.Perfume, perfume_id)


def test_obtener_perfumes_filtrados(
    override_marca_session,
    override_perfume_session
):
    marca1 = obtener_objeto_marca(override_marca_session, "Dior")
    marca2 = obtener_objeto_marca(override_marca_session, "Chanel")
    
    obtener_perfume_precio(override_perfume_session, marca1.id, 10)
    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 47)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca1.id, 50)
    obtener_perfume_precio(override_perfume_session, marca1.id, 70)
    obtener_perfume_precio(override_perfume_session, marca2.id, 47)
    obtener_perfume_precio(override_perfume_session, marca2.id, 70)
    
    consulta_perfumes = perfumes_service.obtener_perfumes(nombre_marca="diO", precio_min=45, precio_max=50)
    
    assert len(consulta_perfumes) == 2
    
    perfumes_ids = [perfume.id for perfume in consulta_perfumes]
    assert perfume1.id in perfumes_ids
    assert perfume2.id in perfumes_ids


def test_obtener_perfumes_rango_precio_incorrecto(
    override_perfume_session
):
    with pytest.raises(perfumes_exception.FiltroPrecioInvalidoError) as error:
        perfumes_service.obtener_perfumes(precio_min=45, precio_max=10)
    
    assert str(error.value) == "El precio minimo debe ser menor que el maximo"
    

def test_obtener_perfumes_ordenados(
    override_marca_session,
    override_perfume_session
):
    marca1 = obtener_objeto_marca(override_marca_session, "Dior")
    
    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 100)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca1.id, 417)
    perfume3 = obtener_perfume_precio(override_perfume_session, marca1.id, 50)
    
    resultado_consulta = perfumes_service.obtener_perfumes(ordenar_por="precio", direccion="DESC")
    
    assert len(resultado_consulta) == 3
    assert resultado_consulta[0].id == perfume2.id
    assert resultado_consulta[1].id == perfume1.id
    assert resultado_consulta[2].id == perfume3.id

def test_obtener_perfumes_ordenados_criterio_invalido():
    with pytest.raises(perfumes_exception.CriterioDeOrdenacionInvalidaError) as error:
        perfumes_service.obtener_perfumes(ordenar_por="stock")
    
    assert str(error.value) == "Criterio de ordenación inválido"
    
def test_obtener_perfumes_ordenados_direccion_ordenacion_invalida():
    with pytest.raises(perfumes_exception.DireccionDeOrdenacionInvalidaError) as error:
        perfumes_service.obtener_perfumes(direccion="izquierda")
    
    assert str(error.value) == "Dirección de ordenación inválida"
    

def test_aplicar_descuento(
    override_marca_session,
    override_perfume_session
):
    marca = obtener_objeto_marca(override_marca_session, "Dior")
    
    precio = Decimal("100.00")
    perfume = obtener_perfume_precio(override_perfume_session, marca.id, precio)
    
    descuento = 20
    perfume_con_descuento = perfumes_service.administrar_descuento(perfume.id, descuento)
    
    
    assert perfume_con_descuento.descuento == descuento
    assert perfume_con_descuento.precio_final == Decimal("80.00")


def test_borrar_descuento(
    override_marca_session,
    override_perfume_session
):
    marca = obtener_objeto_marca(override_marca_session, "Dior")
    
    precio = Decimal("100.00")
    perfume = obtener_perfume_precio(override_perfume_session, marca.id, precio)
    
    descuento = 20
    perfumes_service.administrar_descuento(perfume.id, descuento)
    
    descuento = None
    perfume_sin_descuento = perfumes_service.administrar_descuento(perfume.id, descuento)
    
    assert perfume_sin_descuento.descuento is None
    assert perfume_sin_descuento.precio_final == precio
    

def test_aplicar_descuento_incorrecto(
    override_marca_session,
    override_perfume_session
):
    marca = obtener_objeto_marca(override_marca_session, "Dior")
    
    precio = Decimal("100.00")
    perfume = obtener_perfume_precio(override_perfume_session, marca.id, precio)
    
    descuento = -20
    
    with pytest.raises(perfumes_exception.DescuentoInvalidoError) as error:
        perfumes_service.administrar_descuento(perfume.id, descuento)
    
    assert str(error.value) == "El descuento debe ser mayor de 0 y menor de 100"


def test_aplicar_descuento_perfume_inexistente(
    override_perfume_session
):    

    perfume_id = 13455
    descuento = 20
    
    with pytest.raises(perfumes_exception.PerfumeNoEncontradoError) as error:
        perfumes_service.administrar_descuento(perfume_id, descuento)
    
    assert str(error.value) == f"No se ha encontrado el perfume con el id: {perfume_id}"
    
    