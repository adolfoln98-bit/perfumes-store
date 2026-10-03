import pytest
import models

from fastapi import HTTPException
from services import usuarios_service
from security import dependencies


def test_obtener_admin_actual_user(override_usuario_session):
    
    email = "test@test.com"
    password = "1234abcd"
    
    id_usuario = usuarios_service.crear_usuario(email, password)
    
    usuario = usuarios_service.obtener_usuario_por_id(id_usuario)
    
    assert usuario.rol == models.RolUsuario.USER
    
    with pytest.raises(HTTPException) as error:
        dependencies.obtener_admin_actual(usuario_actual=usuario) 
    
    assert error.value.status_code == 403

def test_obtener_admin_actual_admin(override_usuario_session):
    
    email = "test@test.com"
    password = "1234abcd"
    
    id_usuario = usuarios_service.crear_usuario(email, password)
    
    usuarios_service.modificar_rol(id_usuario, models.RolUsuario.ADMIN)
    
    usuario = usuarios_service.obtener_usuario_por_id(id_usuario)
    
    assert usuario.rol == models.RolUsuario.ADMIN
    

    admin = dependencies.obtener_admin_actual(usuario_actual=usuario) 
    
    assert id_usuario == admin.id