from models import LineaPedido

def crear_linea_pedido(session, pedido_id, perfume_id, nombre_perfume, cantidad, precio_unidad):
    
    linea_pedido = LineaPedido(
        pedido_id = pedido_id,
        perfume_id = perfume_id,
        nombre_perfume=nombre_perfume,
        cantidad = cantidad,
        precio_unidad = precio_unidad
    )
    
    session.add(linea_pedido)
    
    return linea_pedido