from fastapi import APIRouter, HTTPException, Depends

from schemas import marcas as marcas_schema
from services import marcas_service
from exceptions import marcas as marcas_exception

from security import dependencies

marcas_router = APIRouter(
    prefix="/marcas",
    tags=["marcas"]
)

@marcas_router.post("", status_code=201, response_model=marcas_schema.MarcaResponse)

def crear_marca(
    marca: marcas_schema.MarcaCreate,
    admin_actual = Depends(dependencies.obtener_admin_actual)
    ):
    try:
        id_nueva_marca = marcas_service.crear_marca(marca.nombre)
    
    except marcas_exception.MarcaDuplicadaError as error:
        raise HTTPException(status_code=409, detail=str(error))
    
    return marcas_service.obtener_marca_por_id(id_nueva_marca)


@marcas_router.get("", status_code=200, response_model=list[marcas_schema.MarcaResponse])

def obtener_marcas():
    return marcas_service.obtener_marcas()


@marcas_router.get("/{id_marca}", status_code=200, response_model=marcas_schema.MarcaResponse)

def obtener_marca_por_id(id_marca: int):
    
    try:
        marca = marcas_service.obtener_marca_por_id(id_marca)
    
    except marcas_exception.MarcaNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return marca


@marcas_router.patch("/{id_marca}", status_code=200, response_model=marcas_schema.MarcaResponse)

def actualizar_marca(
    id_marca: int,
    marca_update: marcas_schema.MarcaUpdate,
    admin_actual = Depends(dependencies.obtener_admin_actual)
):
    try:
        marca_actualizada = marcas_service.actualizar_marca(id_marca, marca_update.nombre)
    
    except marcas_exception.MarcaDuplicadaError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except marcas_exception.MarcaNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return marca_actualizada


@marcas_router.delete("/{id_marca}", status_code=200)

def eliminar_marca(
    id_marca: int,
    admin_actual = Depends(dependencies.obtener_admin_actual)
):
    try:
        marca_borrada = marcas_service.eliminar_marca(id_marca)
        
    except marcas_exception.MarcaNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return marca_borrada