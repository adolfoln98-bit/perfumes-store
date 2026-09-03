class CantidadInvalidaError(Exception):
    """Se lanza cuando la cantidad de una linea de carrito es incorrecta"""
    
class StockInsuficienteError(Exception):
    """Se lanza cuando la cantidad de un perfume en una linea carrito es mayor al stock disponible"""
    
    