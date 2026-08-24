from fastapi.testclient import TestClient

import main
import models

from decimal import Decimal

from services import usuarios_service, marcas_service, perfumes_service
from security import dependencies

from sqlalchemy import select

cliente = TestClient(main.app)

def crear_usuario(override_usuario_session, email, password="abcd1234"):
    
    id_usuario = usuarios_service.crear_usuario(email, password)
    
    return override_usuario_session.get(models.Usuario, id_usuario)
    
def usuario_admin(override_usuario_session):
    usuario = crear_usuario(override_usuario_session, "admin@test.com")
    
    usuarios_service.modificar_rol(usuario.id, models.RolUsuario.ADMIN)
    
    return override_usuario_session.get(models.Usuario, usuario.id)

def obtener_objeto_marca(override_marca_session, nombre_marca):
    id_marca = marcas_service.crear_marca(nombre_marca)
    return marcas_service.obtener_marca_por_id(id_marca)


def test_crear_perfume(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
    ):
    admin = usuario_admin(override_usuario_session)
    
    marca = obtener_objeto_marca(override_marca_session, "test")
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    nombre_perfume = "perfume_test"
    volumen = 50
    precio_json = 100
    precio = Decimal("100.00")
    stock = 0
    try:
        response = cliente.post("/api/perfumes", json={
            "nombre": nombre_perfume,
            "volumen_ml": volumen,
            "marca_id": marca.id,
            "precio": precio_json,
            "stock": stock
        })
        
        assert response.status_code == 201
        
        datos = response.json()
        
        assert datos["nombre"] == nombre_perfume
        assert datos["volumen_ml"] == volumen
        assert datos["marca_id"] == marca.id
        assert datos["precio"] == str(precio)
        assert datos["stock"] == stock
        assert datos["marca"]["id"] == marca.id
        assert datos["marca"]["nombre"] == "test"
        
        nuevo_perfume = override_perfume_session.get(
            models.Perfume,
            datos["id"]
            )
        
        assert nuevo_perfume is not None
        
        assert nuevo_perfume.nombre  == nombre_perfume
        assert nuevo_perfume.volumen_ml  == volumen
        assert nuevo_perfume.marca_id  == marca.id
        assert nuevo_perfume.precio  == precio
        assert nuevo_perfume.stock  == stock
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        

def test_crear_perfume_marca_inexistente(
    override_usuario_session,
    override_perfume_session
    ):
    admin = usuario_admin(override_usuario_session)
    
    id_marca = 1231
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    nombre_perfume = "perfume_test"
    volumen = 50
    precio_json = 100
    stock = 0
    
    try:
        response = cliente.post("/api/perfumes", json={
            "nombre": nombre_perfume,
            "volumen_ml": volumen,
            "marca_id": id_marca,
            "precio": precio_json,
            "stock": stock
        })
        
        assert response.status_code == 404
        
        datos = response.json()
        assert datos["detail"] == "La marca no existe"
        
        consulta = select(models.Perfume).where(models.Perfume.nombre == nombre_perfume)
        resultado = override_perfume_session.execute(consulta)
                
        assert len(resultado.scalars().all()) == 0
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
    
        
def test_obtener_perfumes(override_marca_session, override_perfume_session):
    
    marca1 = obtener_objeto_marca(override_marca_session, "test1")
    marca2 = obtener_objeto_marca(override_marca_session, "test2")
    
    perfume1 = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca1.id,
        "precio": 50
    }
    
    perfume2={
        "nombre": "perfume2",
        "volumen_ml": 100,
        "marca_id": marca2.id,
        "precio": 75
    }
    perfumes_service.crear_perfume(
        perfume1["nombre"],
        perfume1["volumen_ml"],
        perfume1["marca_id"],
        perfume1["precio"]
        )
    
    perfumes_service.crear_perfume(
        perfume2["nombre"],
        perfume2["volumen_ml"],
        perfume2["marca_id"],
        perfume2["precio"]
        )
    response = cliente.get("/api/perfumes")
    
    assert response.status_code == 200
    
    datos = response.json()
    assert len(datos) == 2
    
    nombres_perfumes = {perfume["nombre"] for perfume in datos}
    assert {"perfume1", "perfume2"} == nombres_perfumes
    
    volumen_perfumes = {perfume["volumen_ml"] for perfume in datos}
    assert {50, 100} == volumen_perfumes
    
    nombre_marcas = {perfume["marca"]["nombre"] for perfume in datos}
    assert {"test1", "test2"} == nombre_marcas
    
    precio_perfumes = {perfume["precio"] for perfume in datos}
    assert {"50.00", "75.00"} == precio_perfumes
    

def test_obtener_perfumes_por_id(override_marca_session, override_perfume_session):
    
    marca = obtener_objeto_marca(override_marca_session, "test")
    
    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"]
        )
    
    response = cliente.get(f"/api/perfumes/{id_perfume}")
    
    assert response.status_code == 200
    
    datos = response.json()
    
    assert datos["id"] == id_perfume
    assert datos["nombre"] == perfume["nombre"]
    assert datos["volumen_ml"] == perfume["volumen_ml"]
    assert datos["marca_id"] == marca.id
    assert datos["precio"] == "50.00"
    assert datos["stock"] == 0
    assert datos["marca"]["id"] == marca.id
    assert datos["marca"]["nombre"] == "test"
    

def test_obtener_perfume_por_id_inexistente(override_perfume_session):
    
    id_perfume = 2223
    
    response = cliente.get(f"/api/perfumes/{id_perfume}")
    
    assert response.status_code == 404
    
    datos = response.json()
    
    assert datos["detail"] == f"No se ha encontrado el perfume con el id: {id_perfume}"
    
    
def test_admin_actualiza_solo_precio_perfume(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
    ):
    admin = usuario_admin(override_usuario_session)
    
    marca = obtener_objeto_marca(override_marca_session, "test1")

    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"]
        )
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}", json={
            "precio": 150
        })
        
        assert response.status_code == 200
        
        datos = response.json()
        
        assert datos["precio"] == "150.00"
        
        assert datos["id"] == id_perfume
        assert datos["nombre"] == perfume["nombre"]
        assert datos["volumen_ml"] == perfume["volumen_ml"]
        assert datos["marca_id"] == perfume["marca_id"]
        assert datos["stock"] == 0
        
        perfume_actualizado = override_perfume_session.get(models.Perfume, id_perfume)
        
        assert perfume_actualizado.nombre == perfume["nombre"]
        assert perfume_actualizado.volumen_ml == perfume["volumen_ml"]
        assert perfume_actualizado.marca_id == perfume["marca_id"]
        assert perfume_actualizado.precio == Decimal("150.00")
        assert perfume_actualizado.stock == 0
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]


def test_admin_actualiza_nombre_y_id_marca(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
):
    admin = usuario_admin(override_usuario_session)
        
    marca1 = obtener_objeto_marca(override_marca_session, "test")
    marca2 = obtener_objeto_marca(override_marca_session, "test2")
    
    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca1.id,
        "precio": 50
        }
        
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"]
        )
        
    def obtener_admin():
            return admin
        
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
        
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}", json={
            "nombre": "nombre actualizado",
            "marca_id": marca2.id
            })
        assert response.status_code == 200
        
        datos = response.json()
        
        assert datos["id"] == id_perfume
        assert datos["nombre"] == "nombre actualizado"
        assert datos["volumen_ml"] == perfume["volumen_ml"]
        assert datos["precio"] == "50.00"
        assert datos["marca_id"] == marca2.id
        assert datos["stock"] == 0
        assert datos["marca"]["id"] == marca2.id
        assert datos["marca"]["nombre"] == "test2"
        
        perfume_actualizado = override_perfume_session.get(models.Perfume, id_perfume)
        
        assert perfume_actualizado.nombre == "nombre actualizado"
        assert perfume_actualizado.volumen_ml == perfume["volumen_ml"]
        assert perfume_actualizado.marca_id == marca2.id
        assert perfume_actualizado.precio == Decimal("50.00")
        assert perfume_actualizado.stock == 0
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]


def test_admin_actualiza_id_marca_invalido(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
):
    admin = usuario_admin(override_usuario_session)
    
    marca  = obtener_objeto_marca(override_marca_session, "test")
    
    id_marca = 125324
    
    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50
        }
        
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"]
        )
        
    def obtener_admin():
            return admin
        
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
        
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}", json={
            "nombre": "nuevo nombre",
            "volumen_ml": 233,
            "marca_id": id_marca
            })
        assert response.status_code == 404
        
        perfume_actualizado = override_perfume_session.get(models.Perfume, id_perfume)
        
        assert perfume_actualizado.nombre == perfume["nombre"]
        assert perfume_actualizado.volumen_ml == perfume["volumen_ml"]
        assert perfume_actualizado.marca_id == marca.id
        
        datos = response.json()
        
        assert datos["detail"] == "La marca no existe"
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        

def test_admin_actualiza_perfume_id_invalido(override_usuario_session, override_perfume_session):
    
    admin = usuario_admin(override_usuario_session)
    
    id_perfume = 1314
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}",json={
            "nombre": "nuevo nombre"
        })
        
        assert response.status_code == 404
        
        datos = response.json()
        assert datos["detail"] == f"No se ha encontrado el perfume con el id: {id_perfume}"
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        

def test_admin_actualiza_null(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
    ):
    admin = usuario_admin(override_usuario_session)
    
    marca = obtener_objeto_marca(override_marca_session, "test1")

    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"]
        )
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}", json={
            "nombre": None
        })
        
        assert response.status_code == 422
        
        
        perfume_persistido = override_perfume_session.get(models.Perfume, id_perfume)
        
        assert perfume_persistido.nombre == perfume["nombre"]
        assert perfume_persistido.volumen_ml == perfume["volumen_ml"]
        assert perfume_persistido.marca_id == perfume["marca_id"]
        assert perfume_persistido.precio == Decimal("50.00")
        assert perfume_persistido.stock == 0
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]


def test_admin_actualiza_body_vacio(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
    ):
    admin = usuario_admin(override_usuario_session)
    
    marca = obtener_objeto_marca(override_marca_session, "test1")

    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"]
        )
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}", json={})
        
        assert response.status_code == 422
        
        
        perfume_persistido = override_perfume_session.get(models.Perfume, id_perfume)
        
        assert perfume_persistido.nombre == perfume["nombre"]
        assert perfume_persistido.volumen_ml == perfume["volumen_ml"]
        assert perfume_persistido.marca_id == perfume["marca_id"]
        assert perfume_persistido.precio == Decimal("50.00")
        assert perfume_persistido.stock == 0
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        

def test_admin_actualiza_precio_invalido(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
    ):
    admin = usuario_admin(override_usuario_session)
    
    marca = obtener_objeto_marca(override_marca_session, "test1")

    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"]
        )
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}", json={
            "precio": 0
        })
        
        assert response.status_code == 422
        
        
        perfume_persistido = override_perfume_session.get(models.Perfume, id_perfume)
        
        assert perfume_persistido.nombre == perfume["nombre"]
        assert perfume_persistido.volumen_ml == perfume["volumen_ml"]
        assert perfume_persistido.marca_id == perfume["marca_id"]
        assert perfume_persistido.precio == Decimal("50.00")
        assert perfume_persistido.stock == 0
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]

def test_admin_repone_stock(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
):
    admin = usuario_admin(override_usuario_session)
    
    marca = obtener_objeto_marca(override_marca_session, "test1")
    
    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50,
        "stock": 19
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"],
        perfume["stock"]
        )
    cantidad_a_sumar = 50
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}/stock",json={
            "cantidad": cantidad_a_sumar
        })
        
        assert response.status_code == 200
        
        datos = response.json()
        
        assert datos["stock"] == perfume["stock"] + cantidad_a_sumar
        
        perfume_actualizado = override_perfume_session.get(models.Perfume, id_perfume)
        
        assert perfume_actualizado.stock == perfume["stock"] + cantidad_a_sumar
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        
    
def test_admin_repone_stock_invalido(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
):
    admin = usuario_admin(override_usuario_session)
    
    marca = obtener_objeto_marca(override_marca_session, "test1")
    
    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50,
        "stock": 19
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"],
        perfume["stock"]
        )
    cantidad_a_sumar = 0
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}/stock",json={
            "cantidad": cantidad_a_sumar
        })
        
        assert response.status_code == 422
        
        
        perfume_actualizado = override_perfume_session.get(models.Perfume, id_perfume)
        
        assert perfume_actualizado.stock == perfume["stock"]
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
    

def test_admin_repone_stock_perfume_inexistente(
    override_usuario_session,
    override_perfume_session
):
    admin = usuario_admin(override_usuario_session)
       
    id_perfume = 1334
    cantidad_a_sumar = 50
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}/stock",json={
            "cantidad": cantidad_a_sumar
        })
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == f"No se ha encontrado el perfume con el id: {id_perfume}"
             
               
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        
        
def test_admin_elimina_perfume(
    override_usuario_session,
    override_marca_session,
    override_perfume_session
):
    admin = usuario_admin(override_usuario_session)
    
    marca = obtener_objeto_marca(override_marca_session, "test1")
    
    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50,
        "stock": 19
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"],
        perfume["stock"]
        )
    
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.delete(f"/api/perfumes/{id_perfume}")
        
        assert response.status_code == 200
        
        datos = response.json()
        
        assert datos == "El perfume ha sido borrado correctamente"
        
        assert override_perfume_session.get(models.Perfume, id_perfume) is None
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        
def test_admin_elimina_perfume_inexistente(
    override_usuario_session,
    override_perfume_session
):
    admin = usuario_admin(override_usuario_session)
    
    id_perfume = 4346
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.delete(f"/api/perfumes/{id_perfume}")
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == f"No se ha encontrado el perfume con el id: {id_perfume}"
        
                
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        

def test_no_admin_intenta_manipular_bdd(
    override_usuario_session,
    override_perfume_session,
    override_marca_session
):
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    marca = obtener_objeto_marca(override_marca_session, "test")
    
    perfume = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": 50,
        "stock": 19
    }
    def obtener_usuario():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario
    
    try:
        response = cliente.post("/api/perfumes", json={
                "nombre": perfume["nombre"],
                "volumen_ml": perfume["volumen_ml"],
                "marca_id": marca.id,
                "precio": perfume["precio"],
                "stock": perfume["stock"]
            })
        
        assert response.status_code == 403
        
        datos = response.json()
        
        assert datos["detail"] == "No tienes los permisos necesarios"
        
        consulta = select(models.Perfume).where(models.Perfume.nombre == perfume["nombre"])
        resultado = override_perfume_session.execute(consulta)
                
        assert len(resultado.scalars().all()) == 0
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
