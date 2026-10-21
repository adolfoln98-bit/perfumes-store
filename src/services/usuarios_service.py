from db import get_session
from exceptions import usuarios as usuarios_exception
from psycopg.errors import UniqueViolation
from repositories import usuarios_repository
from security import password as password_security
from sqlalchemy.exc import IntegrityError

import models



def crear_usuario(email, password):

    email_normalizado = email.strip().lower()

    if not email_normalizado:
        raise usuarios_exception.EmailInvalidoError("El email no puede estar vacio")

    if len(password) < 8:
        raise usuarios_exception.PasswordInvalidaError("La contraseña introducida no es valida")

    if len(password.encode("utf-8")) > 72:
        raise usuarios_exception.PasswordInvalidaError("La contraseña introducida no es valida")

    password_hash = password_security.hashear_password(password)

    with get_session() as session:
        try:
            usuario = usuarios_repository.crear_usuario(
                session,
                email_normalizado,
                password_hash
                )

            session.flush()
            id_usuario = usuario.id

            session.commit()

        except IntegrityError as error:
            session.rollback()
            if isinstance(error.orig, UniqueViolation):
                raise usuarios_exception.EmailYaRegistradoError(
                    f"El email {email_normalizado} ya esta registrado"
                    ) from error
            raise

    return id_usuario

def login_usuario(email, password):

    email_normalizado = email.strip().lower()

    with get_session() as session:
        usuario = usuarios_repository.obtener_usuario_por_email(session, email_normalizado)
        if not usuario:
            raise usuarios_exception.CredencialesInvalidasError("Las credenciales no son correctas")

        if not password_security.verificar_password(password, usuario.password_hash):
            raise usuarios_exception.CredencialesInvalidasError("Las credenciales no son correctas")

    return usuario

def obtener_usuario_por_id(id_usuario):

    with get_session() as session:
        usuario = usuarios_repository.obtener_usuario_por_id(session, id_usuario)

        if usuario is None:
            raise usuarios_exception.UsuarioNoEncontradoError("No se ha encontrado ningun usuario")

    return usuario

def modificar_rol(id_usuario, nuevo_rol, id_superadmin):

    if not isinstance(nuevo_rol, models.RolUsuario):
        raise usuarios_exception.RolInvalidoError("El rol no es correcto")

    if nuevo_rol == models.RolUsuario.SUPERADMIN:
        raise usuarios_exception.AsignacionSuperadminNoPermitidaError("No se puede asignar un superadministrador por este metodo")

    if id_usuario == id_superadmin:
        raise usuarios_exception.ModificacionRolPropioError("No es posible modificar tu propio rol")

    with get_session() as session:
        usuario = usuarios_repository.obtener_usuario_por_id(session, id_usuario)

        if usuario is None:
            raise usuarios_exception.UsuarioNoEncontradoError("No se ha encontrado ningun usuario")

        if usuario.rol == models.RolUsuario.SUPERADMIN:
            raise usuarios_exception.ModificacionSuperadminError("No se puede modificar el rol de un superadministrador")

        usuarios_repository.modificar_rol(usuario, nuevo_rol)

        session.flush()
        session.commit()
