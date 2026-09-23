from db import get_session
from services import (
    carritos_service,
    perfumes_service
)
from repositories import (
    pedidos_repository,
    linea_pedido_repository,
    perfumes_repository,
    linea_carrito_repository
)
from exceptions import carrito as carrito_exception
from exceptions import linea_carrito as linea_carrito_exception

def _calcular_precio_total(pedido):
    
    precio_total = 0
    for linea_pedido in pedido.lineas_pedido:
        precio_linea_pedido = linea_pedido.cantidad * linea_pedido.precio_unidad
        precio_total += precio_linea_pedido
    
    return precio_total


def realizar_pedido(usuario_id):
    
    with get_session() as session:
        carrito = carritos_service._obtener_carrito_por_usuario(session, usuario_id)
        
        if not carrito.lineas_carrito:
            raise carrito_exception.CarritoVacioError("El carrito esta vacio")
        
    
        for linea_carrito in carrito.lineas_carrito:
            if linea_carrito.cantidad > linea_carrito.perfume.stock:
                 raise linea_carrito_exception.StockInsuficienteError("No hay stock suficiente")
        
        try:     
            pedido = pedidos_repository.crear_pedido(session, usuario_id)
            session.flush()
            pedido_id = pedido.id
        
            for linea_carrito in carrito.lineas_carrito:
                linea_pedido_repository.crear_linea_pedido(
                    session,
                    pedido_id,
                    linea_carrito.perfume_id,
                    linea_carrito.perfume.nombre,
                    linea_carrito.cantidad,
                    linea_carrito.perfume.precio
                )
                perfumes_repository.descontar_stock(linea_carrito.perfume, linea_carrito.cantidad)
            
            for linea_carrito in carrito.lineas_carrito:
                linea_carrito_repository.eliminar_linea_carrito(session, linea_carrito)
        
            session.commit()
        
        except Exception:
            session.rollback()
            raise
    
    with get_session() as session:
        pedido_completo = pedidos_repository.obtener_pedido_completo_por_id(session, pedido_id)
        precio_pedido_completo = _calcular_precio_total(pedido_completo)
        
    return pedido_completo, precio_pedido_completo


def recuperar_pedidos_por_usuario(usuario_id):
    lista_pedidos_completa = []
    with get_session() as session:
        pedidos = pedidos_repository.recuperar_pedidos_por_usuario(session, usuario_id)
        
        for pedido in pedidos:
            lista_pedidos_completa.append(
                (pedido, _calcular_precio_total(pedido))
            )
            
    return lista_pedidos_completa