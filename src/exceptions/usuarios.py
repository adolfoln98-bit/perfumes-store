class EmailInvalidoError(Exception):
    """Se lanza cuando el email no tiene un formato correcto"""

class PasswordInvalidaError(Exception):
    """Se lanza cuando la contraseña no cumple con los parametros estipulados"""

class EmailYaRegistradoError(Exception):
    """Se lanza cuando un email ya ha sido registrado"""

class CredencialesInvalidasError(Exception):
    """Se lanza cuando alguna de las credenciales de inicio de sesion no son correctos"""

class UsuarioNoEncontradoError(Exception):
    """Se lanza cuando la busqueda de usuario no arroja ningun resultado"""

class RolInvalidoError(Exception):
    """Se lanza cuando el rol de usuario no coincide con los estipulados"""

class ModificacionRolPropioError(Exception):
    """Se lanza cuando un superadmin intenta modificar su propio rol"""

class ModificacionSuperadminError(Exception):
    """Se lanza cuando se intenta cambiar el rol de un superadmin"""

class AsignacionSuperadminNoPermitidaError(Exception):
    """Se lanza cuando se intenta modficar el rol a superadmin"""
