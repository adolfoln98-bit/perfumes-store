from fastapi.testclient import TestClient

import main
from services import usuarios_service
from security import dependencies
import models


cliente = TestClient(main.app)

def crear_usuario(override_usuario_session, email, password="abcd1234"):

    id_usuario = usuarios_service.crear_usuario(email, password)

    return override_usuario_session.get(models.Usuario, id_usuario)

def usuario_superadmin(override_usuario_session):
    usuario = crear_usuario(override_usuario_session, "superadmin@test.com")

    usuario.rol = models.RolUsuario.SUPERADMIN
    override_usuario_session.commit()
    override_usuario_session.expire_all()
    return usuario

def test_superadmin_modifica_rol_usuario(override_usuario_session):
    superadmin = usuario_superadmin(override_usuario_session)

    def obtener_superadmin():
        return superadmin

    main.app.dependency_overrides[dependencies.obtener_superadmin_actual] = obtener_superadmin

    usuario_user = crear_usuario(override_usuario_session, "user@test.com")
    try:
        response = cliente.patch(f"/api/usuarios/{usuario_user.id}/rol", json={
            "rol": "admin"
        })

        assert response.status_code == 200

        datos = response.json()

        assert datos["id"] == usuario_user.id
        assert datos["rol"] == "admin"

        override_usuario_session.expire_all()
        usuario_modificado = override_usuario_session.get(models.Usuario, usuario_user.id)

        assert usuario_modificado.rol == models.RolUsuario.ADMIN
    finally:
        del main.app.dependency_overrides[dependencies.obtener_superadmin_actual]



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

        override_usuario_session.expire_all()
        usuario_modificado = override_usuario_session.get(models.Usuario, usuario2.id)

        assert usuario_modificado.rol == models.RolUsuario.USER

    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]

def test_admin_modifica_rol_usuario_inexistente(override_usuario_session):
    superadmin = usuario_superadmin(override_usuario_session)

    def obtener_superadmin():
        return superadmin

    main.app.dependency_overrides[dependencies.obtener_superadmin_actual] = obtener_superadmin

    try:
        response = cliente.patch(f"/api/usuarios/{9999999}/rol", json={
            "rol": "admin"
        })

        assert response.status_code == 404

        datos = response.json()

        assert datos["detail"] == "No se ha encontrado ningun usuario"

    finally:
        del main.app.dependency_overrides[dependencies.obtener_superadmin_actual]


def test_admin_modifica_rol_usuario(override_usuario_session):

    admin = crear_usuario(override_usuario_session, "user1@test.com")
    admin.rol = models.RolUsuario.ADMIN
    override_usuario_session.commit()
    override_usuario_session.expire_all()

    def obtener_admin():
            return admin

    main.app.dependency_overrides[dependencies.obtener_usuario_actual] = obtener_admin

    usuario = crear_usuario(override_usuario_session, "user@test.com")

    try:
        response = cliente.patch(f"/api/usuarios/{usuario.id}/rol", json={
                    "rol": "admin"
                })

        assert response.status_code == 403

        override_usuario_session.expire_all()
        usuario_modificado = override_usuario_session.get(models.Usuario, usuario.id)

        assert usuario_modificado.rol == models.RolUsuario.USER

    finally:
        del main.app.dependency_overrides[dependencies.obtener_usuario_actual]


def test_modificar_rol_sin_autenticacion():
    usuario_id = 11347

    response = cliente.patch(f"/api/usuarios/{usuario_id}/rol", json={
                    "rol": "admin"
                })

    assert response.status_code == 401

def test_superadmin_no_puede_modificar_su_propio_rol(override_usuario_session):
    superadmin = usuario_superadmin(override_usuario_session)

    def obtener_superadmin():
        return superadmin

    main.app.dependency_overrides[dependencies.obtener_superadmin_actual] = obtener_superadmin

    try:
        response = cliente.patch(f"/api/usuarios/{superadmin.id}/rol", json={
            "rol": "admin"
        })

        assert response.status_code == 403

        datos = response.json()
        assert datos["detail"] == "No es posible modificar tu propio rol"

    finally:
        del main.app.dependency_overrides[dependencies.obtener_superadmin_actual]


def test_superadmin_no_puede_modificar_otro_superadmin(override_usuario_session):
    superadmin1 = usuario_superadmin(override_usuario_session)

    superadmin2 = crear_usuario(override_usuario_session, "superadmin2@test.com")
    superadmin2.rol = models.RolUsuario.SUPERADMIN
    override_usuario_session.commit()
    override_usuario_session.expire_all()

    def obtener_superadmin():
        return superadmin1

    main.app.dependency_overrides[dependencies.obtener_superadmin_actual] = obtener_superadmin



    try:
        response = cliente.patch(f"/api/usuarios/{superadmin2.id}/rol", json={
            "rol": "admin"
        })

        assert response.status_code == 403

        datos = response.json()
        assert datos["detail"] == "No se puede modificar el rol de un superadministrador"

        assert superadmin2.rol == models.RolUsuario.SUPERADMIN
    finally:
        del main.app.dependency_overrides[dependencies.obtener_superadmin_actual]


def test_superadmin_no_puede_promocionar_a_superadmin(override_usuario_session):
    superadmin = usuario_superadmin(override_usuario_session)

    usuario = crear_usuario(override_usuario_session, "user@test.com")

    def obtener_superadmin():
        return superadmin

    main.app.dependency_overrides[dependencies.obtener_superadmin_actual] = obtener_superadmin



    try:
        response = cliente.patch(f"/api/usuarios/{usuario.id}/rol", json={
            "rol": "superadmin"
        })

        assert response.status_code == 403

        datos = response.json()
        assert datos["detail"] == "No se puede asignar un superadministrador por este metodo"

        assert usuario.rol == models.RolUsuario.USER
    finally:
        del main.app.dependency_overrides[dependencies.obtener_superadmin_actual]


def test_modificar_rol_invalido_http(override_usuario_session):
    superadmin = usuario_superadmin(override_usuario_session)

    usuario = crear_usuario(override_usuario_session, "user@test.com")

    def obtener_superadmin():
        return superadmin

    main.app.dependency_overrides[dependencies.obtener_superadmin_actual] = obtener_superadmin



    try:
        response = cliente.patch(f"/api/usuarios/{usuario.id}/rol", json={
            "rol": "moderador"
        })

        assert response.status_code == 422
        assert usuario.rol == models.RolUsuario.USER

    finally:
        del main.app.dependency_overrides[dependencies.obtener_superadmin_actual]
