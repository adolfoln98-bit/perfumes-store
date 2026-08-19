import pytest

from services import usuarios_service
from services import auth_service
from security import jwt as jwt_security
from models import Usuario
from exceptions import usuarios

def test_autenticar_usuario(override_usuario_session):
    
    email_usuario = "test@correo.com"
    password_usuario = "1234abcd"
    
    id_usuario = usuarios_service.crear_usuario(email_usuario, password_usuario)
    
    usuario = override_usuario_session.get(Usuario, id_usuario)
    
    token_usuario = auth_service.autenticar_usuario(email_usuario, password_usuario)
    
    assert isinstance(token_usuario, str)
    
    datos_usuario = jwt_security.verificar_access_token(token_usuario)
    
    assert usuario.id == datos_usuario["id"]
    assert usuario.rol.value == datos_usuario["rol"]
    
def test_autenticar_usuario_fallido(override_usuario_session):
    
    email_usuario = "test@correo.com"
    password_usuario = "1234abcd"
    
    usuarios_service.crear_usuario(email_usuario, password_usuario)
    
    with pytest.raises(usuarios.CredencialesInvalidasError):
    
        auth_service.autenticar_usuario(email_usuario, "wrong_password")
    