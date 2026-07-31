from services import marcas_service
from exceptions import marcas

def test_crear_marca():
    marca_id = marcas_service.crear_marca("Versace")
    return marca_id

def test_ver_marcas():
    lista_marcas = marcas_service.obtener_marcas()
    for marca in lista_marcas:
        return marca

def test_actualizar_marca():
    try:
        resultado = marcas_service.actualizar_marca(
            id_marca=1,
            nuevo_nombre="Dolce & Gabbana")
        print(f"Actualizacion correcta: {resultado}")
    
    except marcas.MarcaNoEncontradaError as error:
        print(error)
    except marcas.MarcaDuplicadaError as error:
        print(error)
        
def test_eliminar_marca():
    resultado = marcas_service.eliminar_marca(id_marca=4)
    print(resultado)

if __name__ == "__main__":
    #test_crear_marca()
    #test_ver_marcas()
    #test_actualizar_marca()
    test_eliminar_marca()
    