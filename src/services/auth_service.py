from services import usuarios_service
from security import jwt as jwt_security

def autenticar_usuario(email, password):
    
    usuario = usuarios_service.login_usuario(email, password)
    
    access_token = jwt_security.crear_access_token(usuario.id, usuario.rol.value)
    
    return access_token