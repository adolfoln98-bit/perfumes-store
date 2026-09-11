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
from exceptions import carrito as carrito_exception

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

def test_modificar_cantidad(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 100)
    
    linea_carrito_service.agregar_perfume_al_carrito(
        usuario.id,
        perfume.id,
        10
        )
    nueva_cantidad = 6
    carrito_modificado = linea_carrito_service.modificar_cantidad(usuario.id, perfume.id, nueva_cantidad)
    
    assert carrito_modificado is not None
    
    linea = carrito_modificado.lineas_carrito[0]
    assert linea.cantidad == nueva_cantidad
    assert linea.perfume.id == perfume.id
    
    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito_modificado.id, models.LineaCarrito.perfume_id == perfume.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    
    assert resultado is not None
    assert resultado.cantidad == nueva_cantidad

def test_modificar_cantidad_cantidad_mayor_stock(
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
        5
    )
    
    nueva_cantidad = 15
    
    with pytest.raises(linea_carrito_exception.StockInsuficienteError) as error:
        linea_carrito_service.modificar_cantidad(usuario.id, perfume.id, nueva_cantidad)
   
    assert str(error.value) == "No hay stock suficiente"
    
    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none() 
    
    assert resultado is not None
    assert resultado.cantidad == 5
    
def test_modificar_cantidad_cantidad_carrito_inexistente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 10)
    carrito_id = 11443   
    nueva_cantidad = 15
    
    with pytest.raises(carrito_exception.CarritoNoEncontradoError) as error:
        linea_carrito_service.modificar_cantidad(usuario.id, perfume.id, nueva_cantidad)
   
    assert str(error.value) == "El carrito no ha sido encontrado"
    

def test_modificar_cantidad_cantidad_perfume_inexistente(
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
        5
    )
    otro_perfume_id = 124466
    nueva_cantidad = 15
    
    with pytest.raises(perfumes_exception.PerfumeNoEncontradoError) as error:
        linea_carrito_service.modificar_cantidad(usuario.id, otro_perfume_id, nueva_cantidad)
   
    assert str(error.value) == "No se encontro el perfume"
    
    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == otro_perfume_id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none() 
    
    assert resultado is None

def test_modificar_cantidad_cantidad_perfume_no_en_carrito(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "marca test")
    perfume1 = obtener_perfume(override_perfume_session, marca.id, 10)
    carrito = linea_carrito_service.agregar_perfume_al_carrito(
        usuario.id,
        perfume1.id,
        5
    )
    marca2 = obtener_objeto_marca(override_marca_session, "marca 2 test")
    perfume2 = obtener_perfume(override_perfume_session, marca2.id, 10)
    nueva_cantidad = 5
    
    with pytest.raises(linea_carrito_exception.LineaNoEncontradaError) as error:
        linea_carrito_service.modificar_cantidad(usuario.id, perfume2.id, nueva_cantidad)
   
    assert str(error.value) == "No se encontro la linea del carrito"
    
    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume2.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none() 
    
    assert resultado is None

def test_modificar_cantidad_cantidad_nueva_cantidad_invalida(
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
        5
    )
    
    nueva_cantidad = -1
    
    with pytest.raises(linea_carrito_exception.CantidadInvalidaError) as error:
        linea_carrito_service.modificar_cantidad(usuario.id, perfume.id, nueva_cantidad)
   
    assert str(error.value) == "La nueva cantidad es incorrecta"
    
    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none() 
    
    assert resultado is not None
    assert resultado.cantidad == 5

def test_eliminar_perfume_del_carrito(
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
        5
    )
    carrito_linea_borrada = linea_carrito_service.eliminar_perfume_del_carrito(usuario.id, perfume.id)
    
    assert  carrito_linea_borrada.lineas_carrito == []
    assert carrito.id == carrito_linea_borrada.id
    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito_linea_borrada.id, models.LineaCarrito.perfume_id == perfume.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    
    assert resultado is None


def test_eliminar_perfume_del_carrito_carrito_inexistente(
    override_usuario_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    perfume_id = 12445
        
    with pytest.raises(carrito_exception.CarritoNoEncontradoError) as error:
        linea_carrito_service.eliminar_perfume_del_carrito(usuario.id, perfume_id)
    
    assert str(error.value) == "El carrito no ha sido encontrado"


def test_eliminar_perfume_del_carrito_perfume_no_en_carrito(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca1 = obtener_objeto_marca(override_marca_session, "marca test1")
    perfume1 = obtener_perfume(override_perfume_session, marca1.id, 10)

    marca2 = obtener_objeto_marca(override_marca_session, "marca test2")
    perfume2 = obtener_perfume(override_perfume_session, marca2.id, 10)
  
    carrito = linea_carrito_service.agregar_perfume_al_carrito(
        usuario.id,
        perfume1.id,
        5
    )
    with pytest.raises(linea_carrito_exception.LineaNoEncontradaError) as error:
        linea_carrito_service.eliminar_perfume_del_carrito(usuario.id, perfume2.id)
    
    assert str(error.value) == "No se encontro la linea del carrito"
    
    consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume1.id)
    resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
    
    assert resultado is not None
    assert resultado.perfume_id == perfume1.id