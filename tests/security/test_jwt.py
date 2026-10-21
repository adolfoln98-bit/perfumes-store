import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from security import jwt as jwt_security
from exceptions import auth




def test_crear_access_token():

    id_usuario = 1


    access_token = jwt_security.crear_access_token(id_usuario)

    assert isinstance(access_token, str)

    token_decoded = jwt_security.verificar_access_token(access_token)

    assert token_decoded["id"] == id_usuario

def test_access_token_invalido():

    id_usuario = 1


    access_token = jwt_security.crear_access_token(id_usuario)+"abcdf"

    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)

def test_token_caducado():
    id_usuario = 1


    access_token = jwt_security.crear_access_token(id_usuario, -1)

    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)

def test_token_incompleto_expiracion():
    id_usuario = 1

    payload =  {
        "sub": str(id_usuario),
    }
    access_token = jwt.encode(payload, jwt_security.SECRET_KEY, algorithm=jwt_security.ALGORITHM)

    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)

def test_token_incompleto_sub():

    expiracion = datetime.now(timezone.utc) + timedelta(
    minutes=jwt_security.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload =  {
        "exp": expiracion,
    }
    access_token = jwt.encode(payload, jwt_security.SECRET_KEY, algorithm=jwt_security.ALGORITHM)

    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)


def test_token_sub_no_numerico():

    usuario_id = "wrong"
    expiracion = datetime.now(timezone.utc) + timedelta(
    minutes=jwt_security.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload =  {
        "sub": usuario_id,
        "exp": expiracion,
    }
    access_token = jwt.encode(payload, jwt_security.SECRET_KEY, algorithm=jwt_security.ALGORITHM)

    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)

def test_token_sub_tipo_invalido():

    usuario_id = True
    expiracion = datetime.now(timezone.utc) + timedelta(
    minutes=jwt_security.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload =  {
        "sub": usuario_id,
        "exp": expiracion,
    }
    access_token = jwt.encode(payload, jwt_security.SECRET_KEY, algorithm=jwt_security.ALGORITHM)

    with pytest.raises(auth.TokenInvalidoError):
        jwt_security.verificar_access_token(access_token)
