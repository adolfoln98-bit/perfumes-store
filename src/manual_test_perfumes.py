from services import perfumes_service
from exceptions import perfumes

def test_crear_perfume():
    perfume_id = perfumes_service.crear_perfume("Chanel Nº5", 50, 1)
    print(perfume_id)

def test_crear_perfume_invalido():
    perfume_id = perfumes_service.crear_perfume("Perfume invalido", 50, 2222)
    print(perfume_id)
    
def test_obtener_perfumes():
    perfumes = perfumes_service.obtener_perfumes()
    print(perfumes)

def test_obtener_perfume_id():
    perfume = perfumes_service.obtener_perfume_por_id(2)
    print(perfume, perfume.marca.nombre)

def test_obtener_perfume_por_id_invalido():
    perfume = perfumes_service.obtener_perfume_por_id(122443)
    print(perfume)

def test_actualizar_perfume():
    perfume = perfumes_service.actualizar_perfume(7, "Dior Homme", 100, 2)
    print(perfume)

def test_actualizar_perfume_invalido():
    perfume = perfumes_service.actualizar_perfume(1, "No Existe", 100, 2)
    print(perfume)

def test_actualizar_perfume_marca_invalida():
    perfume = perfumes_service.actualizar_perfume(7, "Dior Homme", 100, 12345)
    print(perfume)

def test_eliminar_perfume():
    perfume = perfumes_service.eliminar_perfume(12)
    print(perfume)
    
def test_eliminar_perfume_invalido():
    perfume = perfumes_service.eliminar_perfume(123456)
    print(perfume)

if __name__ == "__main__":
    #test_crear_perfume()
    #test_crear_perfume_invalido()
    #test_obtener_perfumes()
    #test_obtener_perfume_id()
    #test_obtener_perfume_por_id_invalido()
    #test_actualizar_perfume()
    #test_actualizar_perfume_invalido()
    #test_actualizar_perfume_marca_invalida()
    #test_eliminar_perfume()
    test_eliminar_perfume_invalido()