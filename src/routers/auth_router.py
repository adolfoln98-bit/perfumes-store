from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from schemas import auth as auth_schema
from services import auth_service
from exceptions import usuarios as usuarios_exception

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@auth_router.post("/login", status_code=200, response_model=auth_schema.Token)

def login_usuario(form_data=Depends(OAuth2PasswordRequestForm)):
    try:
        access_token = auth_service.autenticar_usuario(form_data.username, form_data.password)
        
    except usuarios_exception.CredencialesInvalidasError as error:
            raise HTTPException(
                status_code=401,
                detail=str(error),
                headers={"WWW-Authenticate": "Bearer"}
                )
        
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }