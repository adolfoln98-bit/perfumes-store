from fastapi import APIRouter, Depends, HTTPException

from schemas import pedidos as pedidos_schema
from security import dependencies
from services import pedidos_service

from exceptions import carrito as carrito_exception
from exceptions import linea_carrito as linea_carrito_exception

pedidos_router = APIRouter(
    prefix="/pedidos",
    tags=["pedidos"]
)

@pedidos_router.post("", status_code=201, response_model=pedidos_schema.PedidoResponse)

def realizar_pedido(
    usuario = Depends(dependencies.obtener_usuario_actual)
):
    try:
        pedido, precio_total = pedidos_service.realizar_pedido(usuario.id)
    except carrito_exception.CarritoNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except (
        carrito_exception.CarritoVacioError,
        linea_carrito_exception.StockInsuficienteError
    ) as error:
        raise HTTPException(status_code=409, detail=str(error))
    
    return {
        "id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "fecha_creacion": pedido.fecha_creacion,
        "lineas_pedido": pedido.lineas_pedido,
        "precio_total": precio_total
    }


@pedidos_router.get("", status_code=200, response_model=list[pedidos_schema.PedidoResponse])

def obtener_pedidos(
    usuario = Depends(dependencies.obtener_usuario_actual)
):
    
    pedidos = pedidos_service.recuperar_pedidos_por_usuario(usuario.id)
    
    lista_respuesta = []
    
    for (pedido, precio_total) in pedidos:
        lista_respuesta.append(
            {
                "id": pedido.id,
                "usuario_id": pedido.usuario_id,
                "fecha_creacion": pedido.fecha_creacion,
                "lineas_pedido": pedido.lineas_pedido,
                "precio_total": precio_total
            }
        )
    return lista_respuesta
    