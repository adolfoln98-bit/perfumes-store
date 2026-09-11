from fastapi import APIRouter, Depends, HTTPException

from schemas import carrito as carritos_schema
from security import dependencies
from services import linea_carrito_service, carritos_service

from exceptions import perfumes as perfumes_exception
from exceptions import linea_carrito as linea_carrito_exception
from exceptions import usuarios as usuarios_exception
from exceptions import carrito as carrito_exception

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

@carritos_router.get("", status_code=200, response_model=carritos_schema.CarritoResponse)
def obtener_carrito(
    usuario = Depends(dependencies.obtener_usuario_actual)    
):
    try:
        carrito = carritos_service.obtener_carrito_por_usuario(usuario.id)
    
    except carrito_exception.CarritoNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return carrito

@carritos_router.patch("/perfumes/{perfume_id}", status_code=200, response_model=carritos_schema.CarritoResponse)
def modificar_cantidad(
    perfume_id: int,
    modificacion: carritos_schema.ModificarCantidadLineaCarritoRequest,
    usuario = Depends(dependencies.obtener_usuario_actual)
):
    try:
        carrito = linea_carrito_service.modificar_cantidad(usuario.id, perfume_id, modificacion.cantidad)
    
    except(
        carrito_exception.CarritoNoEncontradoError,
        perfumes_exception.PerfumeNoEncontradoError,
        linea_carrito_exception.LineaNoEncontradaError
    ) as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    except linea_carrito_exception.StockInsuficienteError as error:
        raise HTTPException(status_code=409, detail=str(error))
    
    return carrito

@carritos_router.delete("/perfumes/{perfume_id}", status_code=200, response_model= carritos_schema.CarritoResponse)

def eliminar_perfume_del_carrito(
    perfume_id: int,
    usuario = Depends(dependencies.obtener_usuario_actual)
):
    try:
        carrito = linea_carrito_service.eliminar_perfume_del_carrito(usuario.id, perfume_id)
        
    except(
        carrito_exception.CarritoNoEncontradoError,
        linea_carrito_exception.LineaNoEncontradaError
    ) as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return carrito