import models

from services import(
    marcas_service,
    perfumes_service
)

from repositories import perfumes_repository

def obtener_objeto_marca(override_marca_session, nombre_marca):
    id_marca = marcas_service.crear_marca(nombre_marca)
    
    return override_marca_session.get(models.Marca, id_marca)

def obtener_perfume(override_perfume_session, id_marca, stock):
    datos_perfume = {
            "nombre": "perfume",
            "volumen_ml": 50,
            "marca_id": id_marca,
            "precio": 50,
            "stock": stock
        }
    perfume_id = perfumes_service.crear_perfume(
            datos_perfume["nombre"],
            datos_perfume["volumen_ml"],
            datos_perfume["marca_id"],
            datos_perfume["precio"],
            datos_perfume["stock"]
            )
    
    return override_perfume_session.get(models.Perfume, perfume_id)

def obtener_perfume_precio(override_perfume_session, id_marca, precio):
    datos_perfume = {
            "nombre": "perfume",
            "volumen_ml": 50,
            "marca_id": id_marca,
            "precio": precio,
            "stock": 10
        }
    perfume_id = perfumes_service.crear_perfume(
            datos_perfume["nombre"],
            datos_perfume["volumen_ml"],
            datos_perfume["marca_id"],
            datos_perfume["precio"],
            datos_perfume["stock"]
            )
    
    return override_perfume_session.get(models.Perfume, perfume_id)

def obtener_perfume_nombre(override_perfume_session, id_marca, nombre):
    datos_perfume = {
            "nombre": nombre,
            "volumen_ml": 50,
            "marca_id": id_marca,
            "precio": 75,
            "stock": 10
        }
    perfume_id = perfumes_service.crear_perfume(
            datos_perfume["nombre"],
            datos_perfume["volumen_ml"],
            datos_perfume["marca_id"],
            datos_perfume["precio"],
            datos_perfume["stock"]
            )
    
    return override_perfume_session.get(models.Perfume, perfume_id)

def test_obtener_perfumes(
    override_marca_session,
    override_perfume_session
):
    marca1 = obtener_objeto_marca(override_marca_session, "Dior")
    marca2 = obtener_objeto_marca(override_marca_session, "Chanel")
    
    perfume1 = obtener_perfume(override_perfume_session, marca1.id, 10)
    obtener_perfume(override_perfume_session, marca2.id, 20)
    
    perfume_consulta = perfumes_repository.obtener_perfumes(override_perfume_session, "dio")
    
    assert len(perfume_consulta) == 1
    assert perfume_consulta[0].id == perfume1.id
    assert perfume_consulta[0].marca.nombre == "Dior"


def test_obtener_perfumes_caps_lock(
    override_marca_session,
    override_perfume_session
):
    marca1 = obtener_objeto_marca(override_marca_session, "Dior")
    marca2 = obtener_objeto_marca(override_marca_session, "Chanel")
    
    perfume1 = obtener_perfume(override_perfume_session, marca1.id, 10)
    obtener_perfume(override_perfume_session, marca2.id, 20)
    
    perfume_consulta = perfumes_repository.obtener_perfumes(override_perfume_session, "DIOR")
    
    assert len(perfume_consulta) == 1
    assert perfume_consulta[0].id == perfume1.id
    assert perfume_consulta[0].marca.nombre == "Dior"


def test_obtener_perfumes_precio_min(
    override_marca_session,
    override_perfume_session
):
    marca = obtener_objeto_marca(override_marca_session, "Dior")
    
    obtener_perfume_precio(override_perfume_session, marca.id, 10)
    obtener_perfume_precio(override_perfume_session, marca.id, 45)
    perfume1 = obtener_perfume_precio(override_perfume_session, marca.id, 50)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca.id, 70)

    perfume_consulta = perfumes_repository.obtener_perfumes(override_perfume_session, precio_min=50)
    assert len(perfume_consulta) == 2
    
    perfumes_ids = [perfume.id for perfume in perfume_consulta]
    assert perfume1.id in perfumes_ids
    assert perfume2.id in perfumes_ids


def test_obtener_perfumes_precio_max(
    override_marca_session,
    override_perfume_session
):
    marca = obtener_objeto_marca(override_marca_session, "Dior")
    
    perfume1 = obtener_perfume_precio(override_perfume_session, marca.id, 10)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca.id, 45)
    perfume3 = obtener_perfume_precio(override_perfume_session, marca.id, 50)
    obtener_perfume_precio(override_perfume_session, marca.id, 70)

    perfume_consulta = perfumes_repository.obtener_perfumes(override_perfume_session, precio_max=50)
    assert len(perfume_consulta) == 3
    
    perfumes_ids = [perfume.id for perfume in perfume_consulta]
    assert perfume1.id in perfumes_ids
    assert perfume2.id in perfumes_ids
    assert perfume3.id in perfumes_ids


def test_obtener_perfume_precio_min_y_max(
    override_marca_session,
    override_perfume_session
):
    marca = obtener_objeto_marca(override_marca_session, "Dior")
    
    obtener_perfume_precio(override_perfume_session, marca.id, 10)
    perfume1 = obtener_perfume_precio(override_perfume_session, marca.id, 45)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca.id, 50)
    obtener_perfume_precio(override_perfume_session, marca.id, 70)

    perfume_consulta = perfumes_repository.obtener_perfumes(override_perfume_session,precio_min=45, precio_max=50)
    
    assert len(perfume_consulta) == 2
    
    perfumes_ids = [perfume.id for perfume in perfume_consulta]
    assert perfume1.id in perfumes_ids
    assert perfume2.id in perfumes_ids


def test_obtener_perfume_todos_filtros(
    override_marca_session,
    override_perfume_session
):
    marca1 = obtener_objeto_marca(override_marca_session, "Dior")
    marca2 = obtener_objeto_marca(override_marca_session, "Chanel")
    
    obtener_perfume_precio(override_perfume_session, marca1.id, 10)
    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 47)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca1.id, 50)
    obtener_perfume_precio(override_perfume_session, marca1.id, 70)
    obtener_perfume_precio(override_perfume_session, marca2.id, 47)
    obtener_perfume_precio(override_perfume_session, marca2.id, 70)
    

    perfume_consulta = perfumes_repository.obtener_perfumes(override_perfume_session, nombre_marca= "diO",precio_min=45, precio_max=50)
    
    assert len(perfume_consulta) == 2
    
    perfumes_ids = [perfume.id for perfume in perfume_consulta]
    assert perfume1.id in perfumes_ids
    assert perfume2.id in perfumes_ids


def test_obtener_perfume_ordenados_por_defecto(
    override_marca_session,
    override_perfume_session
):
    nombre_marca1 = "Dior"
    nombre_marca2 = "Chanel"
    nombre_marca3 = "Armani"
    marca1 = obtener_objeto_marca(override_marca_session, nombre_marca1)
    marca2 = obtener_objeto_marca(override_marca_session, nombre_marca2)
    marca3 = obtener_objeto_marca(override_marca_session, nombre_marca3)
    
    perfume1 = obtener_perfume_nombre(override_perfume_session, marca1.id, "Sauvage")
    perfume2 = obtener_perfume_nombre(override_perfume_session, marca2.id, "Chanel Nº5")
    perfume3 = obtener_perfume_nombre(override_perfume_session, marca3.id, "Aqua Di Gio")
    perfume4 = obtener_perfume_nombre(override_perfume_session, marca1.id, "Dior Homme")
    perfume5 = obtener_perfume_nombre(override_perfume_session, marca2.id, "Bleu de Chanel")
    perfume6 = obtener_perfume_nombre(override_perfume_session, marca3.id, "Stronger With You")
    
    perfumes = perfumes_repository.obtener_perfumes(override_perfume_session)
    
    assert len(perfumes) == 6
    
    assert perfumes[0].id == perfume3.id
    assert perfumes[1].id == perfume6.id
    assert perfumes[2].id == perfume5.id
    assert perfumes[3].id == perfume2.id
    assert perfumes[4].id == perfume4.id
    assert perfumes[5].id == perfume1.id

def test_obtener_perfume_ordenados_por_desc(
    override_marca_session,
    override_perfume_session
):
    nombre_marca1 = "Dior"
    nombre_marca2 = "Chanel"
    nombre_marca3 = "Armani"
    marca1 = obtener_objeto_marca(override_marca_session, nombre_marca1)
    marca2 = obtener_objeto_marca(override_marca_session, nombre_marca2)
    marca3 = obtener_objeto_marca(override_marca_session, nombre_marca3)
    
    perfume1 = obtener_perfume_nombre(override_perfume_session, marca1.id, "Sauvage")
    perfume2 = obtener_perfume_nombre(override_perfume_session, marca2.id, "Chanel Nº5")
    perfume3 = obtener_perfume_nombre(override_perfume_session, marca3.id, "Aqua Di Gio")
    perfume4 = obtener_perfume_nombre(override_perfume_session, marca1.id, "Dior Homme")
    perfume5 = obtener_perfume_nombre(override_perfume_session, marca2.id, "Bleu de Chanel")
    perfume6 = obtener_perfume_nombre(override_perfume_session, marca3.id, "Stronger With You")
    
    perfumes = perfumes_repository.obtener_perfumes(override_perfume_session, direccion="desc")
    
    assert len(perfumes) == 6
    
    assert perfumes[0].id == perfume1.id
    assert perfumes[1].id == perfume4.id
    assert perfumes[2].id == perfume2.id
    assert perfumes[3].id == perfume5.id
    assert perfumes[4].id == perfume6.id
    assert perfumes[5].id == perfume3.id

def test_obtener_perfume_ordenados_por_nombre_asc(
    override_marca_session,
    override_perfume_session
):
    nombre_marca1 = "Dior"
    nombre_marca2 = "Chanel"
    nombre_marca3 = "Armani"
    marca1 = obtener_objeto_marca(override_marca_session, nombre_marca1)
    marca2 = obtener_objeto_marca(override_marca_session, nombre_marca2)
    marca3 = obtener_objeto_marca(override_marca_session, nombre_marca3)
    
    perfume1 = obtener_perfume_nombre(override_perfume_session, marca1.id, "Sauvage")
    perfume2 = obtener_perfume_nombre(override_perfume_session, marca2.id, "Chanel Nº5")
    perfume3 = obtener_perfume_nombre(override_perfume_session, marca3.id, "Aqua Di Gio")
    perfume4 = obtener_perfume_nombre(override_perfume_session, marca1.id, "Dior Homme")
    perfume5 = obtener_perfume_nombre(override_perfume_session, marca2.id, "Bleu de Chanel")
    perfume6 = obtener_perfume_nombre(override_perfume_session, marca3.id, "Stronger With You")
    
    perfumes = perfumes_repository.obtener_perfumes(override_perfume_session, ordenar_por="nombre")
    
    assert len(perfumes) == 6
    
    assert perfumes[0].id == perfume3.id
    assert perfumes[1].id == perfume5.id
    assert perfumes[2].id == perfume2.id
    assert perfumes[3].id == perfume4.id
    assert perfumes[4].id == perfume1.id
    assert perfumes[5].id == perfume6.id


def test_obtener_perfume_ordenados_por_precio_desc(
    override_marca_session,
    override_perfume_session
):
    nombre_marca1 = "Dior"
    nombre_marca2 = "Chanel"
    nombre_marca3 = "Armani"
    marca1 = obtener_objeto_marca(override_marca_session, nombre_marca1)
    marca2 = obtener_objeto_marca(override_marca_session, nombre_marca2)
    marca3 = obtener_objeto_marca(override_marca_session, nombre_marca3)
    
    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 120)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca2.id, 80)
    perfume3 = obtener_perfume_precio(override_perfume_session, marca3.id, 60)
    perfume4 = obtener_perfume_precio(override_perfume_session, marca1.id, 100)
    perfume5 = obtener_perfume_precio(override_perfume_session, marca2.id, 110)
    perfume6 = obtener_perfume_precio(override_perfume_session, marca3.id, 82)
    
    perfumes = perfumes_repository.obtener_perfumes(override_perfume_session, ordenar_por="precio", direccion="desc")
    
    assert len(perfumes) == 6
    
    assert perfumes[0].id == perfume1.id
    assert perfumes[1].id == perfume5.id
    assert perfumes[2].id == perfume4.id
    assert perfumes[3].id == perfume6.id
    assert perfumes[4].id == perfume2.id
    assert perfumes[5].id == perfume3.id


def test_obtener_perfumes_con_descuento(
    override_marca_session,
    override_perfume_session
):
    nombre_marca1 = "Dior"
    nombre_marca2 = "Chanel"
    
    marca1 = obtener_objeto_marca(override_marca_session, nombre_marca1)
    marca2 = obtener_objeto_marca(override_marca_session, nombre_marca2)
    
    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 120)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca2.id, 80)

    perfume1.descuento = 20
    override_perfume_session.commit()
    
    perfume_con_descuento = perfumes_repository.obtener_perfumes(override_perfume_session, en_oferta=True)
    
    assert len(perfume_con_descuento) == 1
    assert perfume_con_descuento[0].id == perfume1.id
    

def test_obtener_perfumes_sin_descuento(
    override_marca_session,
    override_perfume_session
):
    nombre_marca1 = "Dior"
    nombre_marca2 = "Chanel"
    
    marca1 = obtener_objeto_marca(override_marca_session, nombre_marca1)
    marca2 = obtener_objeto_marca(override_marca_session, nombre_marca2)
    
    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 120)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca2.id, 80)

    perfume1.descuento = 20
    override_perfume_session.commit()
    
    perfume_sin_descuento = perfumes_repository.obtener_perfumes(override_perfume_session, en_oferta=False)
    
    assert len(perfume_sin_descuento) == 1
    assert perfume_sin_descuento[0].id == perfume2.id
    

def test_obtener_perfumes_precio_final_maximo(
    override_marca_session,
    override_perfume_session
):
    nombre_marca1 = "Dior"
    
    marca = obtener_objeto_marca(override_marca_session, nombre_marca1)
    
    perfume1 = obtener_perfume_precio(override_perfume_session, marca.id, 100)
    obtener_perfume_precio(override_perfume_session, marca.id, 55)

    perfume1.descuento = 50
    override_perfume_session.commit()
    
    perfume_consulta = perfumes_repository.obtener_perfumes(override_perfume_session, precio_max=50)
    assert len(perfume_consulta) == 1
    
    id_perfume = perfume_consulta[0].id
    assert perfume1.id == id_perfume


def test_obtener_perfumes_precio_final_minimo(
    override_marca_session,
    override_perfume_session
):
    nombre_marca1 = "Dior"
    
    marca = obtener_objeto_marca(override_marca_session, nombre_marca1)
    
    perfume1 = obtener_perfume_precio(override_perfume_session, marca.id, 100)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca.id, 70)

    perfume1.descuento = 50
    override_perfume_session.commit()
    
    perfume_consulta = perfumes_repository.obtener_perfumes(override_perfume_session, precio_min=60)
    assert len(perfume_consulta) == 1
    
    id_perfume = perfume_consulta[0].id
    assert perfume2.id == id_perfume


def test_obtener_perfumes_por_precio_final_asc(
    override_marca_session,
    override_perfume_session
):
    
    nombre_marca1 = "Dior"
    nombre_marca2 = "Chanel"

    marca1 = obtener_objeto_marca(override_marca_session, nombre_marca1)
    marca2 = obtener_objeto_marca(override_marca_session, nombre_marca2)

    perfume1 = obtener_perfume_precio(override_perfume_session, marca1.id, 100)
    perfume2 = obtener_perfume_precio(override_perfume_session, marca2.id, 80)
    perfume3 = obtener_perfume_precio(override_perfume_session, marca1.id, 60)

    perfume1.descuento = 50
    override_perfume_session.commit()
    
    perfumes = perfumes_repository.obtener_perfumes(override_perfume_session, ordenar_por="precio", direccion="asc")
    
    assert len(perfumes) == 3
    
    assert perfumes[0].id == perfume1.id
    assert perfumes[1].id == perfume3.id
    assert perfumes[2].id == perfume2.id