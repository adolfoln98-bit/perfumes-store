import models
import pytest
from decimal import Decimal

from services import(
    usuarios_service,
    carritos_service,
    marcas_service,
    perfumes_service,
    linea_carrito_service,
    pedidos_service
    )

from repositories import(
    perfumes_repository,
    carritos_repository,
    pedidos_repository
)

from exceptions import carrito as carrito_exception
from exceptions import linea_carrito as linea_carrito_exception
from exceptions import pedidos as pedidos_exception

from sqlalchemy import select

def crear_usuario(override_usuario_session, email, password="abcd1234"):
    
    id_usuario = usuarios_service.crear_usuario(email, password)
    
    return override_usuario_session.get(models.Usuario, id_usuario)

def obtener_objeto_marca(override_marca_session, nombre_marca):
    id_marca = marcas_service.crear_marca(nombre_marca)
    
    return override_marca_session.get(models.Marca, id_marca)

def obtener_perfume(override_perfume_session, id_marca, stock):
    datos_perfume = {
            "nombre": "perfume",
            "volumen_ml": 50,
            "marca_id": id_marca,
            "precio": 50,
            "stock": stock
        }
    perfume_id = perfumes_service.crear_perfume(
            datos_perfume["nombre"],
            datos_perfume["volumen_ml"],
            datos_perfume["marca_id"],
            datos_perfume["precio"],
            datos_perfume["stock"]
            )
    
    return override_perfume_session.get(models.Perfume, perfume_id)

def agregar_perfume_al_carrito(override_linea_carrito_session, usuario_id, perfume_id, cantidad):
    return linea_carrito_service.agregar_perfume_al_carrito(usuario_id, perfume_id, cantidad)

def test_crear_pedido(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    marca = obtener_objeto_marca(override_marca_session, "test")
    
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    stock_inicial = perfume.stock
    
    cantidad = 15
    carrito = agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume.id, cantidad)
    
    pedido, precio_total = pedidos_service.realizar_pedido(usuario.id)
    
    assert pedido.usuario_id == usuario.id
    assert len(pedido.lineas_pedido) == 1
    
    
    linea_pedido = pedido.lineas_pedido[0]
    
    assert linea_pedido.nombre_perfume == perfume.nombre
    assert linea_pedido.cantidad == cantidad
    assert linea_pedido.perfume_id == perfume.id
    assert linea_pedido.precio_unidad == perfume.precio
    assert linea_pedido.perfume.marca_id == marca.id
    
    assert precio_total == linea_pedido.cantidad * linea_pedido.precio_unidad
    
    perfume_actualizado = perfumes_repository.obtener_perfume_por_id(override_perfume_session, perfume.id)
    assert perfume_actualizado.stock == stock_inicial-cantidad
    
    carrito_actualizado = carritos_repository.obtener_carrito_completo_por_id(override_carrito_session, carrito.id)
    assert len(carrito_actualizado.lineas_carrito) == 0
    
    pedido_persistido = pedidos_repository.obtener_pedido_completo_por_id(override_pedidos_session, pedido.id)
        
    assert pedido_persistido is not None
    assert pedido_persistido.usuario_id == usuario.id
    
    assert len(pedido_persistido.lineas_pedido) == 1
    linea_pedido_bdd = pedido_persistido.lineas_pedido[0]
    assert linea_pedido_bdd.perfume_id == perfume.id
    assert linea_pedido_bdd.nombre_perfume == perfume.nombre
    assert linea_pedido_bdd.cantidad == cantidad
    assert linea_pedido_bdd.precio_unidad == perfume.precio


def test_crear_pedido_carrito_vacio(
    override_usuario_session,
    override_carrito_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    carritos_service._crear_o_obtener_carrito(override_carrito_session, usuario.id)
    
    with pytest.raises(carrito_exception.CarritoVacioError) as error:
        pedidos_service.realizar_pedido(usuario.id)
    
    assert str(error.value) == "El carrito esta vacio"


def test_crear_pedido_carrito_inexistente(
    override_usuario_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    with pytest.raises(carrito_exception.CarritoNoEncontradoError) as error:
        pedidos_service.realizar_pedido(usuario.id)
    
    assert str(error.value) == "El carrito no ha sido encontrado"


def test_crear_pedido_stock_insuficiente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session,
    override_carrito_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    marca = obtener_objeto_marca(override_marca_session, "test")
    
    perfume = obtener_perfume(override_perfume_session, marca.id, 50)
    stock_inicial = perfume.stock
    
    cantidad = 15
    carrito = agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume.id, cantidad)
    
    cantidad_a_descontar = 45
    perfumes_repository.descontar_stock(perfume, cantidad_a_descontar)
    
    with pytest.raises(linea_carrito_exception.StockInsuficienteError) as error:
        pedidos_service.realizar_pedido(usuario.id)
        
    assert str(error.value) == "No hay stock suficiente"
    
    
    carrito_completo = carritos_repository.obtener_carrito_completo_por_id(override_carrito_session, carrito.id)
    assert len(carrito_completo.lineas_carrito) == 1
    linea_carrito = carrito_completo.lineas_carrito[0]
    
    assert linea_carrito.perfume.stock == stock_inicial - cantidad_a_descontar
    assert linea_carrito.cantidad == cantidad
    
    consulta = select(models.Pedido).where(models.Pedido.usuario_id == usuario.id)
    resultado = override_pedidos_session.execute(consulta).scalar_one_or_none()
    
    assert resultado is None
    
    
def test_recuperar_pedidos(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume1 = obtener_perfume(override_perfume_session, marca.id, 150)
    perfume2 = obtener_perfume(override_perfume_session, marca.id, 50)
    
    cantidad_perfume1 = 15
    cantidad_perfume2 = 3
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume1.id, cantidad_perfume1)
    pedidos_service.realizar_pedido(usuario.id)
    
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume2.id, cantidad_perfume2)
    pedidos_service.realizar_pedido(usuario.id)
    
    pedidos = pedidos_service.recuperar_pedidos_por_usuario(usuario.id)
    
    assert len(pedidos) == 2

    ultimo_pedido, precio_total_ultimo_pedido = pedidos[0]
    assert ultimo_pedido.lineas_pedido[0].perfume_id == perfume2.id
    assert ultimo_pedido.lineas_pedido[0].cantidad == cantidad_perfume2
    assert precio_total_ultimo_pedido == cantidad_perfume2 * ultimo_pedido.lineas_pedido[0].precio_unidad
    
    primer_pedido, precio_total_primer_pedido = pedidos[1]
    assert primer_pedido.lineas_pedido[0].perfume_id == perfume1.id
    assert primer_pedido.lineas_pedido[0].cantidad == cantidad_perfume1
    assert precio_total_primer_pedido == cantidad_perfume1 * primer_pedido.lineas_pedido[0].precio_unidad


def test_recuperar_pedido_usuario_sin_pedidos(
    override_usuario_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    pedidos = pedidos_service.recuperar_pedidos_por_usuario(usuario.id)
    
    assert pedidos == []


def test_recuperar_pedido_por_id(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)

    
    cantidad_perfume = 15
  
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume.id, cantidad_perfume)
    pedido, _ = pedidos_service.realizar_pedido(usuario.id)
    
    
    pedido_recuperado, precio_total_pedido_realizado = pedidos_service.recuperar_pedido_por_id(usuario.id, pedido.id)
    
    assert pedido_recuperado.id == pedido.id
    assert pedido_recuperado.usuario_id == usuario.id
    
    linea_pedido = pedido_recuperado.lineas_pedido[0]
    assert linea_pedido.perfume_id == perfume.id
    assert precio_total_pedido_realizado == linea_pedido.precio_unidad * cantidad_perfume


def test_recuperar_pedido_por_id_pedido_inexistente(
    override_usuario_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    pedido_id = 12445
    
    with pytest.raises(pedidos_exception.PedidoNoEncontradoError) as error:
        pedidos_service.recuperar_pedido_por_id(usuario.id, pedido_id)
    
    assert str(error.value) == "El pedido no ha sido encontrado"
    

def test_recuperar_pedido_por_id_usuario_incorrecto(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario1 = crear_usuario(override_usuario_session, "user1@test.com")
    usuario2 = crear_usuario(override_usuario_session, "user2@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)

    
    cantidad_perfume = 15
  
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario1.id, perfume.id, cantidad_perfume)
    pedido, _ = pedidos_service.realizar_pedido(usuario1.id)
    
    with pytest.raises(pedidos_exception.PedidoNoEncontradoError) as error:
        pedidos_service.recuperar_pedido_por_id(usuario2.id, pedido.id)
    
    assert str(error.value) == "El pedido no ha sido encontrado"


def test_crear_pedido_perfume_descontado(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    marca = obtener_objeto_marca(override_marca_session, "test")
    
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    descuento = 50
    perfumes_service.administrar_descuento(perfume.id, descuento)
    
    #precio unidad es de 50 de modo que el 50% es 25
    precio_unidad = Decimal("25.00")
    
    
    cantidad = 15
    
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume.id, cantidad)
    
    pedido, precio_total = pedidos_service.realizar_pedido(usuario.id)
    

    linea_pedido = pedido.lineas_pedido[0]

    assert linea_pedido.precio_unidad == precio_unidad
   
    
    assert precio_total == cantidad * precio_unidad
    