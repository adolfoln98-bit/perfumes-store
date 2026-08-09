from services import usuarios_service

def test_crear_usuario():
    id_usuario = usuarios_service.crear_usuario("adolfo@correo.com", "1234abcd")
    
    print(id_usuario)

def test_crear_usuario_email_normalizado():
    id_usuario = usuarios_service.crear_usuario(
        "   Adolfo123@Correo.com   ",
        "1234abcd"
    )

    print(id_usuario)

def test_crear_usuario_ya_registrado():
    usuarios_service.crear_usuario("adolfo@correo.com", "dcba4321")
    
    
def test_crear_usuario_password_invalida():
    usuarios_service.crear_usuario("adolfo@correo.com", "dcb")
    
    
if __name__ == "__main__":
    #test_crear_usuario()
    #test_crear_usuario_email_normalizado()
    #test_crear_usuario_ya_registrado()
    test_crear_usuario_password_invalida()