from pydantic import BaseModel, EmailStr, Field
import models

class UsuarioBase(BaseModel):
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)
    
class UsuarioResponse(UsuarioBase):
    id: int
    rol: models.RolUsuario


class UsuarioRol(BaseModel):
    rol: models.RolUsuario