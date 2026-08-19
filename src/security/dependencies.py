from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

import models
from security import jwt as jwt_security
from services import usuarios_service

from exceptions import auth as auth_exception
from exceptions import usuarios as usuarios_exception

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def obtener_usuario_actual(token= Depends(oauth2_scheme)):
    
    try:
        token_usuario = jwt_security.verificar_access_token(token)
    
        usuario = usuarios_service.obtener_usuario_por_id(token_usuario["id"])
        
    except (usuarios_exception.UsuarioNoEncontradoError, auth_exception.TokenInvalidoError) as error:
         raise HTTPException(
             status_code=401,
             detail=str(error),
             headers={"WWW-Authenticate": "Bearer"}
             )
    
    return usuario

def obtener_admin_actual(usuario_actual = Depends(obtener_usuario_actual)):
    if usuario_actual.rol != models.RolUsuario.ADMIN:
        raise HTTPException(
            status_code = 403,
            detail = "No tienes los permisos necesarios"
        )
    
    return usuario_actual
    