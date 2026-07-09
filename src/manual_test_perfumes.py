from repositories.perfumes_repository import crear_perfume, obtener_perfumes

id_perfume = crear_perfume("Chanel Nº5", 100, 1)
print(id_perfume)

perfumes = obtener_perfumes()
print(perfumes)

