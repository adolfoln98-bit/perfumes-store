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

def obtener_perfume_precio(override_perfume_session, id_marca, precio):
    datos_perfume = {
            "nombre": "perfume",
            "volumen_ml": 50,
            "marca_id": id_marca,
            "precio": precio,
            "stock": 10
        }
    perfume_id = perfumes_service.crear_perfume(
            datos_perfume["nombre"],
            datos_perfume["volumen_ml"],
            datos_perfume["marca_id"],
            datos_perfume["precio"],
            datos_perfume["stock"]
            )
    
    return override_perfume_session.get(models.Perfume, perfume_id)


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


def test_obtener_perfumes_filtrados(
    override_marca_session,
    override_perfume_session
):
    marca1 = obtener_objeto_marca(override_marca_session, "Dior")
    marca2 = obtener_objeto_marca(override_marca_session, "Chanel")
    
    obtener_perfume_precio(override_perfume_session, marca1.id, 10)
    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 47)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca1.id, 50)
    obtener_perfume_precio(override_perfume_session, marca1.id, 70)
    obtener_perfume_precio(override_perfume_session, marca2.id, 47)
    obtener_perfume_precio(override_perfume_session, marca2.id, 70)
    
    response = cliente.get("/api/perfumes?nombre_marca=diO&precio_min=45&precio_max=50")
    
    assert response.status_code == 200
    
    datos = response.json()
    
    assert len(datos) == 2
    
    perfumes_ids = [perfume["id"] for perfume in datos]
    assert perfume1.id in perfumes_ids
    assert perfume2.id in perfumes_ids

def test_obtener_perfumes_rango_precio_invalido(
    override_perfume_session
):
    response = cliente.get("/api/perfumes?precio_min=45&precio_max=10")
    
    assert response.status_code == 422
    
    datos = response.json()
    
    assert datos["detail"] == "El precio minimo debe ser menor que el maximo"


def test_obtener_perfumes_ordenados_por_precio(
    override_marca_session,
    override_perfume_session
):
    marca1 = obtener_objeto_marca(override_marca_session, "Dior")

    
    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 47)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca1.id, 17)
    perfume3 = obtener_perfume_precio(override_perfume_session, marca1.id, 50)

    response = cliente.get("/api/perfumes?ordenar_por=precio&direccion=desc")
    
    assert response.status_code == 200
    
    datos = response.json()
    
    assert datos[0]["id"] == perfume3.id
    assert datos[1]["id"] == perfume1.id
    assert datos[2]["id"] == perfume2.id


def test_obtener_perfumes_criterio_ordenacion_invalido():    
    response = cliente.get("/api/perfumes?ordenar_por=stock")
    
    assert response.status_code == 422
    
    datos = response.json()
    
    assert datos["detail"] == "Criterio de ordenación inválido"


def test_obtener_perfumes_direccion_ordenacion_invalida():    
    response = cliente.get("/api/perfumes?direccion=izquierda")
    
    assert response.status_code == 422
    
    datos = response.json()
    
    assert datos["detail"] == "Dirección de ordenación inválida"
    

def test_perfume_con_descuento(
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
        "precio": Decimal("100.00"),
        "stock": 100
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"],
        perfume["stock"]
        )
    
    descuento = 20
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}/descuento", json={
            "descuento": descuento
        })
    
        assert response.status_code == 200
    
        datos = response.json()
    
        assert datos["descuento"] == descuento
        assert Decimal(datos["precio_final"]) == Decimal("80.00")
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]


def test_quitar_descuento(
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
        "precio": Decimal("100.00"),
        "stock": 100
    }
    
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"],
        perfume["stock"]
        )
    
    perfumes_service.administrar_descuento(id_perfume, 20)
    descuento = None
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}/descuento", json={
            "descuento": descuento
        })
    
        assert response.status_code == 200
    
        datos = response.json()
    
        assert datos["descuento"] is None
        assert Decimal(datos["precio_final"]) == Decimal("100.00")
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
    

def test_descuento_invalido(
    override_usuario_session,
    override_perfume_session
    ):
    admin = usuario_admin(override_usuario_session)
    id_perfume = 1344
    
    descuento = -20
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}/descuento", json={
            "descuento": descuento
        })
    
        assert response.status_code == 422
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]

def test_descuento_perfume_inexistente(
    override_usuario_session,
    override_perfume_session
    ):
    admin = usuario_admin(override_usuario_session)
    id_perfume = 1344
    
    descuento = 20
    
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}/descuento", json={
            "descuento": descuento
        })
    
        assert response.status_code == 404
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]

def test_no_admin_intenta_agregar_descuento(
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
    id_perfume = perfumes_service.crear_perfume(
        perfume["nombre"],
        perfume["volumen_ml"],
        perfume["marca_id"],
        perfume["precio"],
        perfume["stock"]
        )
    descuento = 20
    
    def obtener_usuario():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario
    
    try:
        response = cliente.patch(f"/api/perfumes/{id_perfume}/descuento", json={
                "descuento": descuento
            })
        
        assert response.status_code == 403
        
        datos = response.json()
        
        assert datos["detail"] == "No tienes los permisos necesarios"
        
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]


def test_obtener_perfumes_con_descuento(
    override_perfume_session,
    override_marca_session 
):
    
    marca = obtener_objeto_marca(override_marca_session, "test1")

    perfume1 = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": Decimal("100.00"),
        "stock": 100
    }
    
    id_perfume1 = perfumes_service.crear_perfume(
        perfume1["nombre"],
        perfume1["volumen_ml"],
        perfume1["marca_id"],
        perfume1["precio"],
        perfume1["stock"]
        )
    
    perfume2 = {
        "nombre": "perfume2",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": Decimal("100.00"),
        "stock": 100
    }
    
    id_perfume2 = perfumes_service.crear_perfume(
        perfume2["nombre"],
        perfume2["volumen_ml"],
        perfume2["marca_id"],
        perfume2["precio"],
        perfume2["stock"]
        )
    
    descuento = 20
    perfumes_service.administrar_descuento(id_perfume1, descuento)
    
    response = cliente.get("/api/perfumes?en_oferta=true")
        
    assert response.status_code == 200
        
    datos = response.json()
    assert len(datos) == 1
    assert datos[0]["id"] == id_perfume1


def test_obtener_perfumes_sin_descuento(
    override_perfume_session,
    override_marca_session 
):
    
    marca = obtener_objeto_marca(override_marca_session, "test1")

    perfume1 = {
        "nombre": "perfume1",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": Decimal("100.00"),
        "stock": 100
    }
    
    id_perfume1 = perfumes_service.crear_perfume(
        perfume1["nombre"],
        perfume1["volumen_ml"],
        perfume1["marca_id"],
        perfume1["precio"],
        perfume1["stock"]
        )
    
    perfume2 = {
        "nombre": "perfume2",
        "volumen_ml": 50,
        "marca_id": marca.id,
        "precio": Decimal("100.00"),
        "stock": 100
    }
    
    id_perfume2 = perfumes_service.crear_perfume(
        perfume2["nombre"],
        perfume2["volumen_ml"],
        perfume2["marca_id"],
        perfume2["precio"],
        perfume2["stock"]
        )
    
    descuento = 20
    perfumes_service.administrar_descuento(id_perfume1, descuento)
    
    response = cliente.get("/api/perfumes?en_oferta=false")
        
    assert response.status_code == 200
        
    datos = response.json()
    assert len(datos) == 1
    assert datos[0]["id"] == id_perfume2