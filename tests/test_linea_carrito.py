import pytest

import models
from services import (
    linea_carrito_service,
    usuarios_service,
    marcas_service,
    perfumes_service
    )
from sqlalchemy import select
from exceptions import linea_carrito as linea_carrito_exception
from exceptions import perfumes as perfumes_exception
from exceptions import usuarios as usuarios_exception

def obtener_usuario(override_usuario_session, email, password="abcd1234"):
    
    id_usuario = usuarios_service.crear_usuario(email, password)
    
    return override_usuario_session.get(models.Usuario, id_usuario)

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

def test_agregar_perfume_al_carrito(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    carrito = linea_carrito_service.agregar_perfume_al_carrito(
        usuario.id,
        perfume.id,
        4
    )
    assert carrito is not None
    
    assert carrito.usuario_id == usuario.id
    
    assert len(carrito.lineas_carrito) == 1
    
    linea = carrito.lineas_carrito[0]
    assert linea.carrito_id == carrito.id
    assert linea.perfume_id == perfume.id
    assert linea.cantidad == 4
    
    assert linea.perfume.id == perfume.id
    
    consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
    resultado = override_linea_carrito_session.execute(consulta)
    
    assert len(resultado.scalars().all()) == 1
    
    consulta2 = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
    resultado2 = override_linea_carrito_session.execute(consulta2).scalar_one_or_none()
    
    assert resultado2 is not None
    assert resultado2.cantidad == 4
    assert resultado2.carrito_id == carrito.id
    assert resultado2.perfume_id == perfume.id


def test_agregar_perfume_existente_al_carrito(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    linea_carrito_service.agregar_perfume_al_carrito(
        usuario.id,
        perfume.id,
        4
    )
    carrito = linea_carrito_service.agregar_perfume_al_carrito(
        usuario.id,
        perfume.id,
        6
    )
    
    assert len(carrito.lineas_carrito) == 1
    
    linea = carrito.lineas_carrito[0]
    assert linea.cantidad == 10
    
    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
    resultado = override_linea_carrito_session.execute(consulta).scalars().all()
    
    assert len(resultado) == 1
    assert resultado[0].carrito_id == carrito.id
    assert resultado[0].perfume_id == perfume.id
    assert resultado[0].cantidad == 10


def test_agregar_perfume_cantidad_invalida(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    with pytest.raises(linea_carrito_exception.CantidadInvalidaError) as error:
        linea_carrito_service.agregar_perfume_al_carrito(
            usuario.id,
            perfume.id,
            0
        )
    assert str(error.value) == "La cantidad es incorrecta"
    
    consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    assert resultado is None
    
        
def test_agregar_perfume_inexistente(
    override_usuario_session,
    override_marca_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    perfume_id = 24256
    
    with pytest.raises(perfumes_exception.PerfumeNoEncontradoError) as error:
        linea_carrito_service.agregar_perfume_al_carrito(
                usuario.id,
                perfume_id,
                5
            )
    assert str(error.value) == "No se encontro el perfume"

    consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    assert resultado is None  


def test_agregar_perfume_stock_insuficiente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 3)
    
    with pytest.raises(linea_carrito_exception.StockInsuficienteError) as error:
        linea_carrito_service.agregar_perfume_al_carrito(
                usuario.id,
                perfume.id,
                5
            )
    assert str(error.value) == "No hay stock suficiente"

    consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    assert resultado is None 
    
def test_agregar_linea_existente_stock_insuficiente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 5)
    
    carrito = linea_carrito_service.agregar_perfume_al_carrito(
            usuario.id,
            perfume.id,
            3
            )
    with pytest.raises(linea_carrito_exception.StockInsuficienteError) as error:
        linea_carrito_service.agregar_perfume_al_carrito(
                usuario.id,
                perfume.id,
                4
            )
    assert str(error.value) == "No hay stock suficiente"

    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    
    assert resultado is not None
    assert resultado.cantidad == 3

def test_agregar_linea_usuario_inexistente(
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario_id = 52325
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    with pytest.raises(usuarios_exception.UsuarioNoEncontradoError) as error:
        linea_carrito_service.agregar_perfume_al_carrito(
                usuario_id,
                perfume.id,
                4
            )
    assert str(error.value) == "No se encontro el usuario"

    consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario_id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    assert resultado is None

def test_agregar_linea_stock_exacto(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 10)
    
    carrito = linea_carrito_service.agregar_perfume_al_carrito(
        usuario.id,
        perfume.id,
        10
        )
    assert carrito is not None
    
    linea = carrito.lineas_carrito[0]
    assert linea.cantidad == 10
    
    consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    
    assert resultado is not None
    assert resultado.id == carrito.id