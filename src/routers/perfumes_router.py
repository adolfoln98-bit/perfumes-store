from fastapi import APIRouter, HTTPException, Depends

from schemas import perfumes as perfumes_schema
from services import perfumes_service
from exceptions import perfumes as perfumes_exception
from exceptions import marcas as marcas_exception
from security import dependencies

perfumes_router = APIRouter(
    prefix="/perfumes",
    tags=["perfumes"]
)

@perfumes_router.post("", status_code=201, response_model=perfumes_schema.PerfumeResponse)

def crear_perfume(
    perfume: perfumes_schema.PerfumeCreate,
    admin_actual = Depends(dependencies.obtener_admin_actual)
):
    try:
        id_nuevo_perfume = perfumes_service.crear_perfume(
            nombre=perfume.nombre,
            volumen_ml=perfume.volumen_ml,
            marca_id=perfume.marca_id,
            precio=perfume.precio,
            stock=perfume.stock
            )
    except marcas_exception.MarcaNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return perfumes_service.obtener_perfume_por_id(id_nuevo_perfume)


@perfumes_router.get("", status_code=200, response_model=list[perfumes_schema.PerfumeResponse])

def obtener_perfumes():
    
    return perfumes_service.obtener_perfumes()


@perfumes_router.get("/{id_perfume}", status_code=200, response_model=perfumes_schema.PerfumeResponse)

def obtener_perfume_por_id(id_perfume: int):
    
    try:
        perfume = perfumes_service.obtener_perfume_por_id(id_perfume)
    except perfumes_exception.PerfumeNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return perfume


@perfumes_router.patch("/{id_perfume}", status_code=200, response_model=perfumes_schema.PerfumeResponse)

def actualizar_perfume(
    id_perfume: int,
    perfume_update: perfumes_schema.PerfumeUpdate,
    admin_actual = Depends(dependencies.obtener_admin_actual)
):
    cambios = perfume_update.model_dump(exclude_unset=True)
    
    try:
        perfume_actualizado = perfumes_service.actualizar_perfume(id_perfume, **cambios)
    
    except (
        perfumes_exception.PerfumeNoEncontradoError,
        marcas_exception.MarcaNoEncontradaError
        ) as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    except perfumes_exception.CampoActualizacionInvalidoError as error:
        raise HTTPException(status_code=422, detail=str(error))
    
    return perfume_actualizado

@perfumes_router.patch("/{id_perfume}/stock", status_code=200, response_model=perfumes_schema.PerfumeResponse)

def reponer_stock(
    id_perfume: int,
    cantidad: perfumes_schema.StockReposicion,
    admin_actual = Depends(dependencies.obtener_admin_actual)
):
    try:
        perfume_stock_actualizado = perfumes_service.reponer_stock(id_perfume, cantidad.cantidad)
        
    except perfumes_exception.PerfumeNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return perfume_stock_actualizado

@perfumes_router.delete("/{id_perfume}", status_code=200)

def eliminar_perfume(
    id_perfume: int,
    admin_actual = Depends(dependencies.obtener_admin_actual)
):
    
    try:
        perfume_borrado = perfumes_service.eliminar_perfume(id_perfume)
        
    except perfumes_exception.PerfumeNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return perfume_borrado