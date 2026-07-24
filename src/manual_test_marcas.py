from services import marcas_service

#marca_id = marcas_service.crear_marca("Versace")
#print(marca_id)

lista_marcas = marcas_service.obtener_marcas()
for marca in lista_marcas:
    print(marca)