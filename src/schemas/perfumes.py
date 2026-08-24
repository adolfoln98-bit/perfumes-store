from pydantic import BaseModel, Field, field_validator, model_validator

from decimal import Decimal
from typing import Optional

from schemas import marcas

class PerfumeBase(BaseModel):
    nombre: str
    volumen_ml: int = Field(..., gt=0)
    precio: Decimal = Field(..., gt=0)
    marca_id: int = Field(..., gt=0)

class PerfumeCreate(PerfumeBase):
    stock: int = Field(0, ge=0)

class PerfumeResponse(PerfumeBase):
    id: int = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    marca: marcas.MarcaResponse

class PerfumeUpdate(BaseModel):
    nombre: Optional[str] = None
    volumen_ml: Optional[int] = Field(None, gt=0)
    precio: Optional[Decimal] = Field(None, gt=0)
    marca_id: Optional[int] = Field(None, gt=0)
    
    @field_validator("nombre", "volumen_ml", "precio", "marca_id")
    @classmethod
    def validar_no_nulo(cls, valor):
        if valor is None:
            raise ValueError("El campo no puede ser null")
    
        return valor
    
    @model_validator(mode="after")
    def validar_algun_campo(self):
        if not self.model_fields_set:
            raise ValueError("Debes proporcionar al menos un campo para actualizar")
    
        return self

class StockReposicion(BaseModel):
    cantidad: int = Field(..., gt=0)