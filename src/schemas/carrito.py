from pydantic import BaseModel, Field

from schemas import perfumes

class AgregarPerfumeCarritoRequest(BaseModel):
    perfume_id: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)

class LineaCarritoResponse(BaseModel):
    id: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    perfume: perfumes.PerfumeResponse

class CarritoResponse(BaseModel):
    id: int = Field(..., gt=0)
    lineas_carrito: list[LineaCarritoResponse]