class CarritoNoEncontradoError(Exception):
    """Se lanza cuando el usuario no tiene un carrito asociado"""

class CarritoVacioError(Exception):
    """Se lanza cuando a la hora de realizar un pedido el carrito esta vacio"""