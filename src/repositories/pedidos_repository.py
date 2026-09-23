from models import Pedido, LineaPedido, Perfume

from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload

def crear_pedido(session, usuario_id):
    pedido = Pedido(
        usuario_id = usuario_id
    )
    
    session.add(pedido)
    
    return pedido

def obtener_pedido_completo_por_id(session, pedido_id):
    
    consulta_pedido = select(Pedido).options(
        joinedload(Pedido.lineas_pedido).
        joinedload(LineaPedido.perfume).
        joinedload(Perfume.marca)
    ).where(Pedido.id == pedido_id)
    
    resultado = session.execute(consulta_pedido)
    
    return resultado.unique().scalar_one_or_none()

def recuperar_pedidos_por_usuario(session, usuario_id):
    consulta_pedido = select(Pedido).options(
        joinedload(Pedido.lineas_pedido)
        ).where(
            Pedido.usuario_id == usuario_id
            ).order_by(
                Pedido.fecha_creacion.desc(),
                Pedido.id.desc()
            )
    
    resultado = session.execute(consulta_pedido)
    
    return resultado.unique().scalars().all()