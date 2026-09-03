from fastapi import APIRouter, Depends, HTTPException

from schemas import carrito as carritos_schema
from security import dependencies
from services import linea_carrito_service

from exceptions import perfumes as perfumes_exception
from exceptions import linea_carrito as linea_carrito_exception
from exceptions import usuarios as usuarios_exception

carritos_router = APIRouter(
    prefix="/carrito",
    tags=["carrito"]
)

@carritos_router.post("/perfumes", status_code=200, response_model=carritos_schema.CarritoResponse)

def agregar_perfume_al_carrito(
    perfume: carritos_schema.AgregarPerfumeCarritoRequest,
    usuario = Depends(dependencies.obtener_usuario_actual)
):
    try:
        carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.perfume_id, perfume.cantidad)
    
    except perfumes_exception.PerfumeNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except linea_carrito_exception.StockInsuficienteError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except usuarios_exception.UsuarioNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return carrito