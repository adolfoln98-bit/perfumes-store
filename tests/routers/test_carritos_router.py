from fastapi.testclient import TestClient

import models
import main

from decimal import Decimal
from services import (
    usuarios_service,
    marcas_service,
    perfumes_service,
    linea_carrito_service
    )
from security import dependencies

from sqlalchemy import select

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

def test_agregar_perfume_al_carrito(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.post("/api/carrito/perfumes", json={
            "perfume_id": perfume.id,
            "cantidad": 10
        })
        
        assert response.status_code == 200
        
        datos = response.json()
        
        assert datos["id"] > 0
        assert len(datos["lineas_carrito"]) == 1
        
        linea = datos["lineas_carrito"][0]
        assert linea["id"] > 0
        assert linea["cantidad"] == 10
        
        perfume_datos = linea["perfume"]
        assert perfume_datos["nombre"] == perfume.nombre
        assert perfume_datos["volumen_ml"] == perfume.volumen_ml
        assert perfume_datos["marca_id"] == marca.id
        assert Decimal(perfume_datos["precio"]) == perfume.precio
        assert perfume_datos["stock"] == perfume.stock
        assert perfume_datos["marca"]["nombre"] == marca.nombre
        
        consulta_carrito = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
        resultado_consulta_carrito = override_linea_carrito_session.execute(consulta_carrito).scalar_one_or_none()
        assert resultado_consulta_carrito is not None
        assert resultado_consulta_carrito.id == datos["id"]
        
        consulta_linea_carrito = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == resultado_consulta_carrito.id, models.LineaCarrito.perfume_id == perfume.id)
        resultado_consulta_linea_carrito = override_linea_carrito_session.execute(consulta_linea_carrito).scalar_one_or_none()
        assert resultado_consulta_linea_carrito is not None
        assert resultado_consulta_linea_carrito.cantidad == 10
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        
    
def test_agregar_perfume_inexistente_al_carrito(
    override_usuario_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    id_perfume = 14234
    
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.post("/api/carrito/perfumes", json={
            "perfume_id": id_perfume,
            "cantidad": 10
        })
        assert response.status_code == 404
        
        datos = response.json()
        assert datos["detail"] == "No se encontro el perfume"
        
        consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        assert resultado is None
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        
    
def test_agregar_perfume_al_carrito_stock_insuficiente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 5)
    
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.post("/api/carrito/perfumes", json={
            "perfume_id": perfume.id,
            "cantidad": 10
        })
        
        assert response.status_code == 409
        
        datos = response.json()
        assert datos["detail"] == "No hay stock suficiente"
        
        consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        assert resultado is None
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
                
    
def test_agregar_perfume_al_carrito_cantidad_menor_igual_cero(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.post("/api/carrito/perfumes", json={
            "perfume_id": perfume.id,
            "cantidad": 0
        })
        
        assert response.status_code == 422
        
        consulta = select(models.Carrito).where(models.Carrito.usuario_id == usuario.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        assert resultado is None
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]

def test_agregar_perfume_al_carrito_usuario_no_autenticado(
    override_marca_session,
    override_perfume_session
):
    
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    
    response = cliente.post("/api/carrito/perfumes", json={
        "perfume_id": perfume.id,
        "cantidad": 10
    })
        
    assert response.status_code == 401

def test_obtener_carrito_por_usuario(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session    
):
    
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    cantidad = 10
    carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.id, cantidad)
    
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.get("/api/carrito")
        
        assert response.status_code == 200
        
        datos = response.json()
        assert datos["id"] == carrito.id

        assert len(datos["lineas_carrito"]) == 1
        
        linea = datos["lineas_carrito"][0]
        assert linea["cantidad"] == cantidad
        
        linea_perfume = linea["perfume"]
        assert linea_perfume["id"] == perfume.id
        assert linea_perfume["marca_id"] == marca.id      
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
           

def test_obtener_carrito_inexistente_por_usuario(
    override_usuario_session,
    override_carrito_session,  
):
    
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
        
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.get("/api/carrito")
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "El carrito no ha sido encontrado"
    
    finally:
         del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
         

def test_obtener_carrito_por_usuario_no_autenticado():
    response = cliente.get("/api/carrito")
        
    assert response.status_code == 401
    

def test_modificar_cantidad(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session    
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    cantidad = 10
    carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.id, cantidad)
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    nueva_cantidad = 25
    
    try:
        response = cliente.patch(f"/api/carrito/perfumes/{perfume.id}", json={
            "cantidad": nueva_cantidad
        })
        
        assert response.status_code == 200
        
        datos = response.json()
        assert datos["id"] == carrito.id
        
        linea = datos["lineas_carrito"][0]
        assert linea["perfume"]["id"] == perfume.id
        assert linea["cantidad"] == nueva_cantidad
        
        consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        
        assert resultado is not None
        assert resultado.cantidad == nueva_cantidad
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        

def test_modificar_cantidad_stock_insuficiente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session    
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 10)
    
    cantidad = 5
    carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.id, cantidad)
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    nueva_cantidad = 25
    
    try:
        response = cliente.patch(f"/api/carrito/perfumes/{perfume.id}", json={
            "cantidad": nueva_cantidad
        })
        
        assert response.status_code == 409
        
        datos = response.json()
        assert datos["detail"] == "No hay stock suficiente"
        
        consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        
        assert resultado is not None
        assert resultado.cantidad == cantidad
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        
def test_modificar_cantidad_stock_insuficiente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session    
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 10)
    
    cantidad = 5
    carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.id, cantidad)
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    nueva_cantidad = 25
    
    try:
        response = cliente.patch(f"/api/carrito/perfumes/{perfume.id}", json={
            "cantidad": nueva_cantidad
        })
        
        assert response.status_code == 409
        
        datos = response.json()
        assert datos["detail"] == "No hay stock suficiente"
        
        consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        
        assert resultado.cantidad == cantidad
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        

def test_modificar_cantidad_carrito_inexistente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session 
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 100)
    nueva_cantidad = 10
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.patch(f"/api/carrito/perfumes/{perfume.id}", json={
            "cantidad": nueva_cantidad
        })
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "El carrito no ha sido encontrado"
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]


def test_modificar_cantidad_perfume_erroneo(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session  
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 100)
    
    cantidad = 5
    linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.id, cantidad)
    perfume2_id = 12131
    nueva_cantidad = 10
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.patch(f"/api/carrito/perfumes/{perfume2_id}", json={
            "cantidad": nueva_cantidad
        })
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "No se encontro el perfume"
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]

def test_modificar_cantidad_perfume_no_en_linea_carrito(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session  
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca1 = obtener_objeto_marca(override_marca_session, "test1")
    marca2 = obtener_objeto_marca(override_marca_session, "test2")
    perfume1 = obtener_perfume(override_perfume_session, marca1.id, 100)
    perfume2 = obtener_perfume(override_perfume_session, marca2.id, 100)
    cantidad = 5
    linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume1.id, cantidad)
    nueva_cantidad = 10
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.patch(f"/api/carrito/perfumes/{perfume2.id}", json={
            "cantidad": nueva_cantidad
        })
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "No se encontro la linea del carrito"
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        

def test_modificar_cantidad_cantidad_invalida(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_carrito_session,
    override_linea_carrito_session  
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test1")
    perfume = obtener_perfume(override_perfume_session, marca.id, 100)
 
    cantidad = 5
    carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.id, cantidad)
    nueva_cantidad = 0
    def obtener_usuario_actual():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    try:
        response = cliente.patch(f"/api/carrito/perfumes/{perfume.id}", json={
            "cantidad": nueva_cantidad
        })
        
        assert response.status_code == 422
        
        consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        
        assert resultado is not None
        assert resultado.cantidad == cantidad
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        

def test_modificar_cantidad_usuario_no_autenticado():
    perfume_id = 12312
    nueva_cantidad = 33
    
    response = cliente.patch(f"/api/carrito/perfumes/{perfume_id}", json={
        "cantidad": nueva_cantidad
    })
        
    assert response.status_code == 401


def test_eliminar_perfume_del_carrito(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session    
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    cantidad = 10
    carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume.id, cantidad)
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    
    try:
        response = cliente.delete(f"/api/carrito/perfumes/{perfume.id}")
        
        assert response.status_code == 200
        
        datos = response.json()
        assert datos["id"] == carrito.id
        
        linea = datos["lineas_carrito"]
        assert linea == []
        
        consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        
        assert resultado is None
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
    

def test_eliminar_perfume_del_carrito_carrito_inexistente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,  
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume = obtener_perfume(override_perfume_session, marca.id, 150)
    
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    
    try:
        response = cliente.delete(f"/api/carrito/perfumes/{perfume.id}")
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "El carrito no ha sido encontrado"
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        

def test_eliminar_perfume_del_carrito_linea_inexistente(
    override_usuario_session,
    override_marca_session,
    override_perfume_session,
    override_linea_carrito_session    
):
    usuario = obtener_usuario(override_usuario_session, "user@test.com")
    marca = obtener_objeto_marca(override_marca_session, "test")
    perfume1 = obtener_perfume(override_perfume_session, marca.id, 150)
    perfume2 = obtener_perfume(override_perfume_session, marca.id, 100)
    
    cantidad = 10
    carrito = linea_carrito_service.agregar_perfume_al_carrito(usuario.id, perfume1.id, cantidad)
    
    def obtener_usuario_actual():
        return usuario
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario_actual
    
    
    try:
        response = cliente.delete(f"/api/carrito/perfumes/{perfume2.id}")
        
        assert response.status_code == 404
        
        datos = response.json()
       
        assert datos["detail"] == "No se encontro la linea del carrito"
        
        consulta = select(models.LineaCarrito).where(models.LineaCarrito.carrito_id == carrito.id, models.LineaCarrito.perfume_id == perfume1.id)
        resultado = override_linea_carrito_session.execute(consulta).scalar_one_or_none()
        
        assert resultado is not None
        assert resultado.perfume_id == perfume1.id
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
    

def test_eliminar_perfume_del_carrito_usuario_no_autenticado():
    perfume_id = 12345
    
    response = cliente.delete(f"/api/carrito/perfumes/{perfume_id}")
        
    assert response.status_code == 401
