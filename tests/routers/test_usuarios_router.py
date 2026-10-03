from fastapi.testclient import TestClient

import main
from services import usuarios_service
from security import dependencies
import models


cliente = TestClient(main.app)

def crear_usuario(override_usuario_session, email, password="abcd1234"):
    
    id_usuario = usuarios_service.crear_usuario(email, password)
    
    return override_usuario_session.get(models.Usuario, id_usuario)
    
def usuario_admin(override_usuario_session):
    usuario = crear_usuario(override_usuario_session, "admin@test.com")
    
    usuarios_service.modificar_rol(usuario.id, models.RolUsuario.ADMIN)
    
    return override_usuario_session.get(models.Usuario, usuario.id)

def test_admin_modifica_rol_usuario(override_usuario_session):
    admin = usuario_admin(override_usuario_session)
    
    def obtener_admin():
        return admin

    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin

    usuario_user = crear_usuario(override_usuario_session, "user@test.com")
    try:
        response = cliente.patch(f"/api/usuarios/{usuario_user.id}/rol", json={
            "rol": "admin"
        })
    
        assert response.status_code == 200
    
        datos = response.json()
    
        assert datos["id"] == usuario_user.id
        assert datos["rol"] == "admin"
    
        usuario_modificado = override_usuario_session.get(models.Usuario, usuario_user.id)
    
        assert usuario_modificado.rol == models.RolUsuario.ADMIN
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]
        
        
        
def test_usuario_modifica_rol_usuario(override_usuario_session):
    
    usuario1 = crear_usuario(override_usuario_session, "user1@test.com")
    
    def obtener_usuario():
            return usuario1
    
    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_usuario
    
    usuario2 = crear_usuario(override_usuario_session, "user2@test.com")
    
    try:
        response = cliente.patch(f"/api/usuarios/{usuario2.id}/rol", json={
                    "rol": "admin"
                })
    
        assert response.status_code == 403
        
        usuario_modificado = override_usuario_session.get(models.Usuario, usuario2.id)
        
        assert usuario_modificado.rol == models.RolUsuario.USER
        
    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]
        
def test_admin_modifica_rol_usuario_inexistente(override_usuario_session):
    admin = usuario_admin(override_usuario_session)
    
    def obtener_admin():
        return admin

    main.app.dependency_overrides[dependencies.obtener_admin_actual] = obtener_admin

    try:
        response = cliente.patch(f"/api/usuarios/{9999999}/rol", json={
            "rol": "admin"
        })
    
        assert response.status_code == 404
        
        datos = response.json()
        
        assert datos["detail"] == "No se ha encontrado ningun usuario"
    
    finally:
        del main.app.dependency_overrides[dependencies.obtener_admin_actual]