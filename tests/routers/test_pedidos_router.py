from fastapi.testclient import TestClient

import models
import main

from repositories import perfumes_repository
from services import(
    usuarios_service,
    carritos_service,
    marcas_service,
    perfumes_service,
    linea_carrito_service,
    pedidos_service
    )
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select

from security import dependencies

cliente = TestClient(main.app)

def obtener_usuario(override_usuario_session, email, password="abcd1234"):
    
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


def test_realizar_pedido(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    cantidad = 15
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume.id, cantidad)
    
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.post("/api/pedidos")
        
        assert response.status_code == 201
        
        datos = response.json()
        
        assert datos["id"] > 0
        assert datos["usuario_id"] == usuario.id
        fecha_creacion = datetime.fromisoformat(datos["fecha_creacion"])
        assert isinstance(fecha_creacion, datetime)
        assert len(datos["lineas_pedido"]) == 1
        
        linea_pedido = datos["lineas_pedido"][0]
        assert linea_pedido["perfume_id"] == perfume.id
        assert linea_pedido["nombre_perfume"] == perfume.nombre
        assert linea_pedido["cantidad"] == cantidad
        assert Decimal(linea_pedido["precio_unidad"]) == perfume.precio
        
        assert Decimal(datos["precio_total"]) == linea_pedido["cantidad"] * Decimal(linea_pedido["precio_unidad"])
        
        consulta = select(models.Pedido).where(models.Pedido.id == datos["id"])
        resultado = override_pedidos_session.execute(consulta).scalar_one_or_none()
        assert resultado is not None
        assert resultado.usuario_id == usuario.id
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        
    
def test_realizar_pedido_sin_carrito(
  override_usuario_session,
  override_pedidos_session  
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    
    def obtener_usuario_actual():
        return usuario
        
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    try:
        response = cliente.post("/api/pedidos")
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "El carrito no ha sido encontrado" 
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        
    
def test_realizar_pedido_carrito_vacio(
  override_usuario_session,
  override_carrito_session,
  override_pedidos_session  
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    carritos_service._crear_o_obtener_carrito(override_carrito_session, usuario.id)
    
    def obtener_usuario_actual():
        return usuario
        
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    try:
        response = cliente.post("/api/pedidos")
        
        assert response.status_code == 409
        
        datos = response.json()
        
        assert datos["detail"] == "El carrito esta vacio" 
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        

def test_realizar_pedido_stock_insuficiente(
  override_usuario_session,
  override_marca_session,
  override_perfume_session,
  override_linea_carrito_session,
  override_pedidos_session  
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 50)
    
    cantidad = 10
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume.id, cantidad)
    
    cantidad_a_descontar = 45
    perfumes_repository.descontar_stock(perfume, cantidad_a_descontar)
    
    def obtener_usuario_actual():
        return usuario
        
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    try:
        response = cliente.post("/api/pedidos")
        
        assert response.status_code == 409
        
        datos = response.json()
        
        assert datos["detail"] == "No hay stock suficiente" 
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        
def test_recuperar_pedido_usuario_sin_pedidos(
    override_usuario_session,
    override_pedidos_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    
    def obtener_usuario_actual():
        return usuario
        
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.get("/api/pedidos")
        
        assert response.status_code == 200
        
        datos = response.json()
        
        assert datos == []
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]


def test_recuperar_pedidos(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume1 = obtener_perfume(override_perfume_session, marca.id, 150)
    perfume2 = obtener_perfume(override_perfume_session, marca.id, 50)
    
    cantidad_perfume1 = 15
    cantidad_perfume2 = 3
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume1.id, cantidad_perfume1)
    pedidos_service.realizar_pedido(usuario.id)
    
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume2.id, cantidad_perfume2)
    pedidos_service.realizar_pedido(usuario.id)
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.get("/api/pedidos")
        
        assert response.status_code == 200
        
        datos = response.json()
        
        assert len(datos) == 2
        pedido_reciente = datos[0]
        linea_reciente = pedido_reciente["lineas_pedido"][0]
        assert linea_reciente["perfume_id"] == perfume2.id
        assert linea_reciente["cantidad"] == cantidad_perfume2
        
        pedido_antiguo = datos[1]
        linea_antigua = pedido_antiguo["lineas_pedido"][0]
        assert linea_antigua["perfume_id"] == perfume1.id
        assert linea_antigua["cantidad"] == cantidad_perfume1

        
        assert Decimal(pedido_reciente["precio_total"]) == Decimal(linea_reciente["precio_unidad"]) * cantidad_perfume2
        assert Decimal(pedido_antiguo["precio_total"]) == Decimal(linea_antigua["precio_unidad"]) * cantidad_perfume1
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]


def test_recuperar_pedido_por_id(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)

    
    cantidad_perfume = 15
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario.id, perfume.id, cantidad_perfume)
    pedido, _ = pedidos_service.realizar_pedido(usuario.id)
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.get(f"/api/pedidos/{pedido.id}")
        
        assert response.status_code == 200

        respuesta_pedido = response.json()
        
        assert respuesta_pedido["id"] == pedido.id
        assert respuesta_pedido["usuario_id"] == usuario.id
        
        linea_pedido = respuesta_pedido["lineas_pedido"][0]
        assert linea_pedido["perfume_id"] == perfume.id
        assert linea_pedido["cantidad"] == cantidad_perfume
        assert Decimal(respuesta_pedido["precio_total"]) == Decimal(linea_pedido["precio_unidad"]) * cantidad_perfume
    finally:
        del  main.app.dependency_overrides[dependencies.obtener_usuario_actual]



def test_recuperar_pedido_por_id_pedido_inexistente(
    override_usuario_session,
    override_pedidos_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    pedido_id = 12445
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.get(f"/api/pedidos/{pedido_id}")
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "El pedido no ha sido encontrado"
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]



def test_recuperar_pedido_por_id_usuario_incorrecto(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session,
    override_pedidos_session
):
    usuario1 = obtener_usuario(override_usuario_session, "user1@test.com")
    usuario2 = obtener_usuario(override_usuario_session, "user2@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)

    
    cantidad_perfume = 15
  
    agregar_perfume_al_carrito(override_linea_carrito_session, usuario1.id, perfume.id, cantidad_perfume)
    pedido, _ = pedidos_service.realizar_pedido(usuario1.id)
    
    def obtener_usuario_actual():
            return usuario2
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.get(f"/api/pedidos/{pedido.id}")
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "El pedido no ha sido encontrado"
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        