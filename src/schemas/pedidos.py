from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

class LineaPedidoResponse(BaseModel):
    perfume_id: int = Field(..., gt=0)
    nombre_perfume: str
    cantidad: int = Field(..., gt=0)
    precio_unidad: Decimal = Field(..., gt=0)
    
class PedidoResponse(BaseModel):
    id: int = Field(..., gt=0)
    usuario_id: int = Field(..., gt=0)
    fecha_creacion: datetime
    lineas_pedido: list[LineaPedidoResponse]
    precio_total: Decimal = Field(..., gt=0)