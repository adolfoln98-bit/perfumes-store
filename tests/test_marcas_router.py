from fastapi.testclient import TestClient

import main
import models

from services import usuarios_service, marcas_service
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


def test_crear_marca(override_usuario_session, override_marca_session):
    admin = usuario_admin(override_usuario_session)
        
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.post("/api/marcas", json={
            "nombre": "cadena test"
        })
    
        assert response.status_code == 201
        
        datos = response.json()
        assert datos["nombre"] == "cadena test"
        
        nueva_marca = override_marca_session.get(models.Marca, datos["id"])
        
        assert nueva_marca is not None
        assert nueva_marca.nombre == "cadena test"
        
    finally:
         del main.app.dependency_overrides[dependencies.obtener_admin_actual]
    

def test_crear_marca_duplicada(override_usuario_session, override_marca_session):
    admin = usuario_admin(override_usuario_session)
        
    def obtener_admin():
        return admin
    
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.post("/api/marcas", json={
            "nombre": "cadena test"
        })
        
        assert response.status_code == 201
        
        datos = response.json()
        assert datos["nombre"] == "cadena test"
        
        nueva_marca = override_marca_session.get(models.Marca, datos["id"])
        
        assert nueva_marca is not None
        assert nueva_marca.nombre == "cadena test"
        
        response_duplicada = cliente.post("/api/marcas", json={
            "nombre": "cadena test"
        })
    
        assert response_duplicada.status_code == 409
        
        consulta = select(models.Marca).where(models.Marca.nombre == "cadena test")
        resultado = override_marca_session.execute(consulta)
        
        assert len(resultado.scalars().all()) == 1
        
    finally:
         del main.app.dependency_overrides[dependencies.obtener_admin_actual]
         

def test_obtener_marcas(override_marca_session):
    
    marcas_service.crear_marca("marca1")
    marcas_service.crear_marca("marca2")
    
    response = cliente.get("/api/marcas")
    
    assert response.status_code == 200
    
    datos = response.json()
    
    assert len(datos) == 2
    
    datos_marcas = {marca["nombre"] for marca in datos}
    assert {"marca1", "marca2"} == datos_marcas
    
    
def test_obtener_marca_por_id(override_marca_session):
    
    id_marca = marcas_service.crear_marca("marca1")
    
    response = cliente.get(f"/api/marcas/{id_marca}")
    
    assert response.status_code == 200
    
    datos = response.json()
    
    assert datos["id"] == id_marca
    assert datos["nombre"] == "marca1"


def test_obtener_marca_inexistente_por_id(override_marca_session):
    
    response = cliente.get("/api/marcas/999999")
    
    assert response.status_code == 404
    
    datos = response.json()
    
    assert datos["detail"] == "No se ha encontrado ninguna marca con el id: 999999"


def test_admin_actualiza_marca(override_usuario_session, override_marca_session):
    
    admin = usuario_admin(override_usuario_session)
    
    id_marca = marcas_service.crear_marca("marca1")
    
    def obtener_admin():
            return admin
        
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.patch(f"/api/marcas/{id_marca}", json={
            "nombre": "nuevo nombre"
        })
        
        assert response.status_code == 200
        
        datos = response.json()
        
        assert datos["nombre"] == "nuevo nombre"
        
        marca_actualizada = override_marca_session.get(models.Marca, id_marca)
        
        assert marca_actualizada.nombre == "nuevo nombre"
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]


def test_admin_actualiza_marca_inexistente(override_usuario_session, override_marca_session):
    
    admin = usuario_admin(override_usuario_session)
    
    def obtener_admin():
                return admin
            
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    id_marca = 1234
    try:
        response = cliente.patch(f"/api/marcas/{id_marca}", json={
                    "nombre": "nuevo nombre"
                })
        
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == f"No se ha encontrado ninguna marca con el id: {id_marca}"
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        

def test_admin_actualiza_marca_duplicada(override_usuario_session, override_marca_session):
    

    
    admin = usuario_admin(override_usuario_session)
    
    def obtener_admin():
        return admin
            
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    marca1 = "marca1"
    marca2 = "marca2"
    
    marcas_service.crear_marca(marca1)
    id_marca_a_cambiar = marcas_service.crear_marca(marca2)
    try:
        response = cliente.patch(f"/api/marcas/{id_marca_a_cambiar}", json={
            "nombre": marca1
        })
        
        assert response.status_code == 409
        
        marca_persistida = override_marca_session.get(models.Marca, id_marca_a_cambiar)
        
        assert marca_persistida.nombre == marca2
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        

def test_eliminar_marca(override_usuario_session, override_marca_session):
    
    admin = usuario_admin(override_usuario_session)
     
    nombre_marca = "marca1"   
    id_marca = marcas_service.crear_marca(nombre_marca)  
        
    def obtener_admin():
            return admin
                
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    
    try:
        response = cliente.delete(f"/api/marcas/{id_marca}")
        
        assert response.status_code == 200
        
        datos = response.json()
        assert datos == "La marca ha sido borrada correctamente"
        
        assert override_marca_session.get(models.Marca, id_marca) is None
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]


def test_eliminar_marca_inexistente(override_usuario_session, override_marca_session):
    
    admin = usuario_admin(override_usuario_session)
    
    def obtener_admin():
            return admin
                
    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin
    id_marca = 1224
    try:
        response = cliente.delete(f"/api/marcas/{id_marca}")
        
        assert response.status_code == 404
        
        datos = response.json()
        assert datos["detail"] == f"No se ha encontrado ninguna marca con el id: {id_marca}"
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]


def test_usuario_no_puede_crear_marca(override_usuario_session, override_marca_session):
    
    usuario = crear_usuario(override_usuario_session, "user@test.com")
    
    def obtener_usuario():
        return usuario
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario
    
    nombre_marca = "nueva marca"
    
    try:
        response = cliente.post("/api/marcas", json={
            "nombre": nombre_marca
        })
        
        assert response.status_code == 403
        
        datos = response.json()
        
        assert datos["detail"] == "No tienes los permisos necesarios"
        
        consulta = select(models.Marca).where(models.Marca.nombre == nombre_marca)
        resultado = override_marca_session.execute(consulta)
        
        assert len(resultado.scalars().all()) == 0
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
    