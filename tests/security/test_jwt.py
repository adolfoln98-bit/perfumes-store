import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from security import jwt as jwt_security
from exceptions import auth




def test_crear_access_token():
         
    id_usuario = 1
    rol_usuario = "user"
    
    
    access_token = jwt_security.crear_access_token(id_usuario, rol_usuario)
    
    assert isinstance(access_token, str)
    
    token_decoded = jwt_security.verificar_access_token(access_token)
    
    assert token_decoded["id"] == id_usuario
    assert token_decoded["rol"] == rol_usuario
    
def test_access_token_invalido():
             
    id_usuario = 1
    rol_usuario = "user"
    
    
    access_token = jwt_security.crear_access_token(id_usuario, rol_usuario)+"abcdf"
    
    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)
        
def test_token_caducado():
    id_usuario = 1
    rol_usuario = "user"
    
    
    access_token = jwt_security.crear_access_token(id_usuario, rol_usuario, -1)
    
    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)
    
def test_token_incompleto_rol():
    
    expiracion = datetime.now(timezone.utc) + timedelta(
    minutes=jwt_security.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    id_usuario = 1
    
    payload =  {
        "sub": str(id_usuario),
        "exp": expiracion,
    }
    access_token = jwt.encode(payload, jwt_security.SECRET_KEY, algorithm=jwt_security.ALGORITHM)
    
    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)

def test_token_incompleto_sub():
    
    expiracion = datetime.now(timezone.utc) + timedelta(
    minutes=jwt_security.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    rol_usuario = "user"
    
    payload =  {
        "rol": rol_usuario,
        "exp": expiracion,
    }
    access_token = jwt.encode(payload, jwt_security.SECRET_KEY, algorithm=jwt_security.ALGORITHM)
    
    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)
        