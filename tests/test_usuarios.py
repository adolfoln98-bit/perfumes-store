import pytest
from fastapi import HTTPException

from services import usuarios_service
from models import Usuario, RolUsuario
from security import password as password_security
from security import dependencies
from exceptions import usuarios
from sqlalchemy import select


def test_crear_usuario(override_usuario_session):
    
    email="correo@correo.com"
    password="abcd1234"
    
    id_usuario = usuarios_service.crear_usuario(
        email,
        password
    )
    
    usuario = override_usuario_session.get(Usuario, id_usuario)

    assert usuario is not None
    assert usuario.email == email.strip().lower()
    assert usuario.password_hash != password
    
    assert password_security.verificar_password(password, usuario.password_hash)
    
    assert usuario.rol.value == "user"
    
def test_crear_usuario_duplcado(override_usuario_session):
    
    email="correo@correo.com"
    password="abcd1234"
    
    usuarios_service.crear_usuario(
        email,
        password
    )
    
    with pytest.raises(usuarios.EmailYaRegistradoError):
        
        usuarios_service.crear_usuario(
            email,
            password
        )
    
    consulta = select(Usuario).where(Usuario.email == email.strip().lower())
    resultado = override_usuario_session.execute(consulta)
    
    assert len(resultado.scalars().all()) == 1
        
def test_password_invalida(override_usuario_session):
    
    email="correo@correo.com"
    password="fail"
    
    with pytest.raises(usuarios.PasswordInvalidaError):
        usuarios_service.crear_usuario(
            email,
            password
        )
    
    consulta = select(Usuario).where(Usuario.email == email.strip().lower())
    resultado = override_usuario_session.execute(consulta)
        
    assert len(resultado.scalars().all()) == 0

def test_password_superior_72_bytes(override_usuario_session):
    
    email="correo@correo.com"
    password="ąćęłńóśźżĄĆĘŁŃÓŚŹŻàèìòùÀÈÌÒÙäëïöüÄËÏÖÜÿ"
    
    assert len(password.encode("utf-8")) > 72
    
    with pytest.raises(usuarios.PasswordInvalidaError):
        usuarios_service.crear_usuario(
            email,
            password
        )
    
    consulta = select(Usuario).where(Usuario.email == email.strip().lower())
    resultado = override_usuario_session.execute(consulta)
        
    assert len(resultado.scalars().all()) == 0

def test_login_usuario(override_usuario_session):
    
    email="correo@correo.com"
    password="abcd1234"
    
    id_usuario =usuarios_service.crear_usuario(
        email,
        password
    )
    
    login = usuarios_service.login_usuario(email, password)
    
    assert login is not None
    
    usuario = override_usuario_session.get(Usuario, id_usuario)
    
    assert usuario.id == login.id
    assert email.strip().lower() == login.email
    
def test_login_usuario_inexistente(override_usuario_session):
    
    email="correo@correo.com"
    password="abcd1234"
    
    with pytest.raises(usuarios.CredencialesInvalidasError):
        usuarios_service.login_usuario(email, password)
        
def test_login_password_invalida(override_usuario_session):
    
    email="correo@correo.com"
    password="abcd1234"
    
    usuarios_service.crear_usuario(
        email,
        password
    )
    
    with pytest.raises(usuarios.CredencialesInvalidasError):
        usuarios_service.login_usuario(email, "wrong_password")
        
def test_obtener_usuario_por_id(override_usuario_session):
    
    email="correo@correo.com"
    password="abcd1234"
    
    id_usuario = usuarios_service.crear_usuario(
        email,
        password
    )
    usuario = usuarios_service.obtener_usuario_por_id(id_usuario)
    
    assert usuario.email == email.strip().lower()
    assert usuario.rol.value == "user"
    
def test_obtener_usuario_por_id_erroneo(override_usuario_session):
    
    with pytest.raises(usuarios.UsuarioNoEncontradoError):
        usuarios_service.obtener_usuario_por_id(0)
        

def test_obtener_admin_actual(override_usuario_session):
    
    email = "test@test.com"
    password = "1234abcd"
    
    id_usuario = usuarios_service.crear_usuario(email, password)
    
    usuario = usuarios_service.obtener_usuario_por_id(id_usuario)
    
    assert usuario.rol == RolUsuario.USER
    
    with pytest.raises(HTTPException) as error:
        dependencies.obtener_admin_actual(usuario_actual=usuario) 
    
    assert error.value.status_code == 403