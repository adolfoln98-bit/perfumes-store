import pytest

from fastapi import HTTPException

from services import usuarios_service
from repositories import usuarios_repository
from models import Usuario, RolUsuario
from security import password as password_security
from security import dependencies
from exceptions import usuarios
from sqlalchemy import select


def test_crear_usuario(override_usuario_session):

    email="correo@correo.com"
    password="abcd1234"

    id_usuario = usuarios_service.crear_usuario(
        email,
        password
    )

    usuario = override_usuario_session.get(Usuario, id_usuario)

    assert usuario is not None
    assert usuario.email == email.strip().lower()
    assert usuario.password_hash != password

    assert password_security.verificar_password(password, usuario.password_hash)

    assert usuario.rol.value == "user"

def test_crear_usuario_duplcado(override_usuario_session):

    email="correo@correo.com"
    password="abcd1234"

    usuarios_service.crear_usuario(
        email,
        password
    )

    with pytest.raises(usuarios.EmailYaRegistradoError):

        usuarios_service.crear_usuario(
            email,
            password
        )

    consulta = select(Usuario).where(Usuario.email == email.strip().lower())
    resultado = override_usuario_session.execute(consulta)

    assert len(resultado.scalars().all()) == 1

def test_password_invalida(override_usuario_session):

    email="correo@correo.com"
    password="fail"

    with pytest.raises(usuarios.PasswordInvalidaError):
        usuarios_service.crear_usuario(
            email,
            password
        )

    consulta = select(Usuario).where(Usuario.email == email.strip().lower())
    resultado = override_usuario_session.execute(consulta)

    assert len(resultado.scalars().all()) == 0

def test_password_superior_72_bytes(override_usuario_session):

    email="correo@correo.com"
    password="ąćęłńóśźżĄĆĘŁŃÓŚŹŻàèìòùÀÈÌÒÙäëïöüÄËÏÖÜÿ"

    assert len(password.encode("utf-8")) > 72

    with pytest.raises(usuarios.PasswordInvalidaError):
        usuarios_service.crear_usuario(
            email,
            password
        )

    consulta = select(Usuario).where(Usuario.email == email.strip().lower())
    resultado = override_usuario_session.execute(consulta)

    assert len(resultado.scalars().all()) == 0

def test_login_usuario(override_usuario_session):

    email="correo@correo.com"
    password="abcd1234"

    id_usuario =usuarios_service.crear_usuario(
        email,
        password
    )

    login = usuarios_service.login_usuario(email, password)

    assert login is not None

    usuario = override_usuario_session.get(Usuario, id_usuario)

    assert usuario.id == login.id
    assert email.strip().lower() == login.email

def test_login_usuario_inexistente(override_usuario_session):

    email="correo@correo.com"
    password="abcd1234"

    with pytest.raises(usuarios.CredencialesInvalidasError):
        usuarios_service.login_usuario(email, password)

def test_login_password_invalida(override_usuario_session):

    email="correo@correo.com"
    password="abcd1234"

    usuarios_service.crear_usuario(
        email,
        password
    )

    with pytest.raises(usuarios.CredencialesInvalidasError):
        usuarios_service.login_usuario(email, "wrong_password")

def test_obtener_usuario_por_id(override_usuario_session):

    email="correo@correo.com"
    password="abcd1234"

    id_usuario = usuarios_service.crear_usuario(
        email,
        password
    )
    usuario = usuarios_service.obtener_usuario_por_id(id_usuario)

    assert usuario.email == email.strip().lower()
    assert usuario.rol.value == "user"

def test_obtener_usuario_por_id_erroneo(override_usuario_session):

    with pytest.raises(usuarios.UsuarioNoEncontradoError):
        usuarios_service.obtener_usuario_por_id(0)


def test_obtener_admin_actual(override_usuario_session):

    email = "test@test.com"
    password = "1234abcd"

    id_usuario = usuarios_service.crear_usuario(email, password)

    usuario = usuarios_service.obtener_usuario_por_id(id_usuario)

    assert usuario.rol == RolUsuario.USER

    with pytest.raises(HTTPException) as error:
        dependencies.obtener_admin_actual(usuario_actual=usuario)

    assert error.value.status_code == 403


def test_superadmin_crea_admin(override_usuario_session):

    email1="correo1@correo.com"
    password1="abcd1234"

    id_usuario1 = usuarios_service.crear_usuario(
        email1,
        password1
    )
    usuario1 = usuarios_service.obtener_usuario_por_id(id_usuario1)
    usuario1.rol = RolUsuario.SUPERADMIN
    override_usuario_session.commit()


    email2="correo2@correo.com"
    password2="dcba4321"

    id_usuario2 = usuarios_service.crear_usuario(
        email2,
        password2
    )
    usuario2 = usuarios_service.obtener_usuario_por_id(id_usuario2)

    assert usuario2.rol == RolUsuario.USER

    usuarios_service.modificar_rol(usuario2.id, RolUsuario.ADMIN, usuario1.id)

    override_usuario_session.expire_all()

    assert usuario2.rol == RolUsuario.ADMIN


def test_superadmin_no_puede_modificar_su_rol(override_usuario_session):

    email1="correo1@correo.com"
    password1="abcd1234"

    id_usuario1 = usuarios_service.crear_usuario(
        email1,
        password1
    )

    usuario1 = usuarios_service.obtener_usuario_por_id(id_usuario1)
    usuario1.rol = RolUsuario.SUPERADMIN
    override_usuario_session.commit()

    assert usuario1.rol == RolUsuario.SUPERADMIN

    with pytest.raises(usuarios.ModificacionRolPropioError) as error:
        usuarios_service.modificar_rol(usuario1.id, RolUsuario.ADMIN, usuario1.id)

    assert str(error.value) == "No es posible modificar tu propio rol"
    assert usuario1.rol == RolUsuario.SUPERADMIN


def test_superadmin_no_puede_modificar_otro_superadmin(override_usuario_session):

    email1="correo1@correo.com"
    password1="abcd1234"

    id_usuario1 = usuarios_service.crear_usuario(
        email1,
        password1
    )

    email2="correo2@correo.com"
    password2="dcba4321"

    id_usuario2 = usuarios_service.crear_usuario(
        email2,
        password2
    )

    usuario1 = usuarios_service.obtener_usuario_por_id(id_usuario1)
    usuario1.rol = RolUsuario.SUPERADMIN

    usuario2 = usuarios_service.obtener_usuario_por_id(id_usuario2)
    usuario2.rol = RolUsuario.SUPERADMIN
    override_usuario_session.commit()


    with pytest.raises(usuarios.ModificacionSuperadminError) as error:
        usuarios_service.modificar_rol(usuario2.id, RolUsuario.ADMIN, usuario1.id)

    assert str(error.value) == "No se puede modificar el rol de un superadministrador"


    override_usuario_session.expire_all()
    assert usuario2.rol == RolUsuario.SUPERADMIN


def test_superadmin_intenta_crear_superadmin(override_usuario_session):

    email1="correo1@correo.com"
    password1="abcd1234"

    id_usuario1 = usuarios_service.crear_usuario(
        email1,
        password1
    )

    email2="correo2@correo.com"
    password2="dcba4321"

    id_usuario2 = usuarios_service.crear_usuario(
        email2,
        password2
    )

    usuario1 = usuarios_service.obtener_usuario_por_id(id_usuario1)
    usuario1.rol = RolUsuario.SUPERADMIN

    usuario2 = usuarios_service.obtener_usuario_por_id(id_usuario2)
    override_usuario_session.commit()


    with pytest.raises(usuarios.AsignacionSuperadminNoPermitidaError) as error:
        usuarios_service.modificar_rol(usuario2.id, RolUsuario.SUPERADMIN, usuario1.id)

    assert str(error.value) == "No se puede asignar un superadministrador por este metodo"


    override_usuario_session.expire_all()
    assert usuario2.rol == RolUsuario.USER


def test_superadmin_intenta_modificar_usuario_inexistente(override_usuario_session):

    email1="correo1@correo.com"
    password1="abcd1234"

    id_usuario1 = usuarios_service.crear_usuario(
        email1,
        password1
    )


    usuario1 = usuarios_service.obtener_usuario_por_id(id_usuario1)
    usuario1.rol = RolUsuario.SUPERADMIN
    usuario2_id = 124352
    override_usuario_session.commit()

    assert usuarios_repository.obtener_usuario_por_id(override_usuario_session, usuario2_id) is None
    with pytest.raises(usuarios.UsuarioNoEncontradoError) as error:
        usuarios_service.modificar_rol(usuario2_id, RolUsuario.ADMIN, usuario1.id)

    assert str(error.value) == "No se ha encontrado ningun usuario"


def test_superadmin_intenta_modificar_usuario_rol_equivocado():

    id_usuario1 = 12344
    id_usuario2 = 56854

    with pytest.raises(usuarios.RolInvalidoError) as error:
        usuarios_service.modificar_rol(id_usuario2, "rol_equivocado", id_usuario1)

    assert str(error.value) == "El rol no es correcto"


def test_superadmin_degrada_admin_a_user(override_usuario_session):

    email1="correo1@correo.com"
    password1="abcd1234"

    id_usuario1 = usuarios_service.crear_usuario(
        email1,
        password1
    )

    email2="correo2@correo.com"
    password2="dcba4321"

    id_usuario2 = usuarios_service.crear_usuario(
        email2,
        password2
    )

    usuario1 = usuarios_service.obtener_usuario_por_id(id_usuario1)
    usuario1.rol = RolUsuario.SUPERADMIN

    usuario2 = usuarios_service.obtener_usuario_por_id(id_usuario2)
    usuario2.rol = RolUsuario.ADMIN
    override_usuario_session.commit()

    assert usuario2.rol == RolUsuario.ADMIN

    usuarios_service.modificar_rol(usuario2.id, RolUsuario.USER, usuario1.id)


    override_usuario_session.expire_all()
    assert usuario2.rol == RolUsuario.USER


def test_login_password_superior_72_bytes(override_usuario_session):

    email="correo1@correo.com"
    password="abcd1234"

    usuarios_service.crear_usuario(
        email,
        password
    )

    wrong_pass = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻàèìòùÀÈÌÒÙäëïöüÄËÏÖÜÿ"
    assert len(wrong_pass.encode("utf-8")) > 72

    with pytest.raises(usuarios.CredencialesInvalidasError) as error:
        usuarios_service.login_usuario(email, wrong_pass)

    assert str(error.value) == "Las credenciales no son correctas"
