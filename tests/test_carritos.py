import pytest

import models
from services import usuarios_service, carritos_service
from exceptions import usuarios as usuarios_exception

from sqlalchemy import select

def crear_usuario(override_usuario_session, email, password="abcd1234"):
    
    id_usuario = usuarios_service.crear_usuario(email, password)
    
    return override_usuario_session.get(models.Usuario, id_usuario)

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