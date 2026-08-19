from models import Usuario
from sqlalchemy import select

def crear_usuario(session, email, password_hash):
    
    usuario = Usuario(
        email = email,
        password_hash = password_hash
    )
    
    session.add(usuario)
    
    return usuario

def obtener_usuario_por_email(session, email):
    consulta_email = select(Usuario).where(Usuario.email == email)
    
    resultado = session.execute(consulta_email)
    
    return resultado.scalar_one_or_none()

def obtener_usuario_por_id(session, id_usuario):
    
    return session.get(Usuario, id_usuario)

def modificar_rol(usuario, nuevo_rol):
    
    usuario.rol = nuevo_rol