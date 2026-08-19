from fastapi import APIRouter, HTTPException, Depends

from services import usuarios_service
from schemas import usuarios as usuarios_schema
from exceptions import usuarios as usuarios_exception
from security import dependencies

usuarios_router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@usuarios_router.post("", status_code=201, response_model=usuarios_schema.UsuarioResponse)

def crear_usuario(usuario: usuarios_schema.UsuarioCreate):
    try:
        id_nuevo_usuario = usuarios_service.crear_usuario(usuario.email, usuario.password)
        
    except usuarios_exception.EmailYaRegistradoError as error:
        raise HTTPException(status_code=409, detail=str(error))
    
    return usuarios_service.obtener_usuario_por_id(id_nuevo_usuario)

@usuarios_router.get("/me", response_model=usuarios_schema.UsuarioResponse)

def obtener_perfil_actual(usuario_actual = Depends(dependencies.obtener_usuario_actual)):
    return usuario_actual


@usuarios_router.patch("/{id_usuario}/rol", response_model=usuarios_schema.UsuarioResponse)

def modificar_rol(
    id_usuario: int,
    rol_usuario: usuarios_schema.UsuarioRol,
    admin_actual = Depends(dependencies.obtener_admin_actual)
    ):
    try:
        usuarios_service.modificar_rol(id_usuario, rol_usuario.rol)
        
    except usuarios_exception.UsuarioNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return usuarios_service.obtener_usuario_por_id(id_usuario)
    