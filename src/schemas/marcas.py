from pydantic import BaseModel

class MarcaBase(BaseModel):
    nombre: str

class MarcaCreate(MarcaBase):
    pass

class MarcaResponse(MarcaBase):
    id: int

class MarcaUpdate(MarcaBase):
    pass