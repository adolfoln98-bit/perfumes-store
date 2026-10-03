import pytest

import models
from services import(
    usuarios_service,
    carritos_service,
    marcas_service,
    perfumes_service,
    linea_carrito_service
    )
from exceptions import usuarios as usuarios_exception
from exceptions import carrito as carrito_exception

from sqlalchemy import select

def crear_usuario(override_usuario_session, email, password="abcd1234"):
    
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

def test_crear_o_obtener_carrito_inexistente(
    override_carrito_session, 
    override_usuario_session
):
    
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    carrito = carritos_service.crear_o_obtener_carrito(usuario.id)
    
    assert carrito is not None
    
    assert carrito.usuario_id == usuario.id
    
    consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
    
    resultado = override_carrito_session.execute(consulta)
    assert len(resultado.scalars().all()) == 1
    
def test_crear_o_obtener_carrito_existente(
    override_carrito_session,
    override_usuario_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
        
    carrito = carritos_service.crear_o_obtener_carrito(usuario.id)
    
    carrito2 = carritos_service.crear_o_obtener_carrito(usuario.id)
    
    assert carrito.id == carrito2.id
    consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
        
    resultado = override_carrito_session.execute(consulta)
    assert len(resultado.scalars().all()) == 1
    
def test_crear_o_obtener_carrito_usuario_invalido(
    override_carrito_session
):
    id_usuario = 23565
    
    with pytest.raises(usuarios_exception.UsuarioNoEncontradoError) as error:
        carritos_service.crear_o_obtener_carrito(id_usuario)
    
    assert str(error.value) == "El usuario no existe"
    
    consulta = select(models.Carrito).where(models.Carrito.usuario_id == id_usuario)
            
    resultado = override_carrito_session.execute(consulta)
    assert len(resultado.scalars().all()) == 0
    

def test_obtener_carrito_por_usuario(
    override_carrito_session,
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    cantidad = 10
    carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.id, cantidad)
    
    carrito_usuario = carritos_service.obtener_carrito_por_usuario(usuario.id)
    
    assert carrito_usuario.id == carrito.id
    
    assert len(carrito_usuario.lineas_carrito) == 1
    
    linea = carrito_usuario.lineas_carrito[0]
    assert linea.cantidad == cantidad
    assert linea.perfume.id == perfume.id
    assert linea.perfume.marca.id == marca.id
    
def test_obtener_carrito_inexistente_por_usuario(
    override_carrito_session,
    override_usuario_session,
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    with pytest.raises(carrito_exception.CarritoNoEncontradoError) as error:  
        carritos_service.obtener_carrito_por_usuario(usuario.id) 
        
    assert str(error.value) == "El carrito no ha sido encontrado"