class PerfumeNoEncontradoError(Exception):
    """Se lanza cuando en la busqueda realizada no aparece ningún perfume en la busqueda"""

class PrecioIncorrectoError(Exception):
    """Se lanza cuando el precio introducido es erroneo"""
    
class StockIncorrectoError(Exception):
    """Se lanza cuando el stock introducido no es correcto"""
    
class CantidadStockIncorrectaError(Exception):
    """Se lanza cuando la nueva cantidad de stock introducida es incorrecta"""
    
class CampoActualizacionInvalidoError(Exception):
    """Se lanza cuando se ha intentado modificar mediante la actualización general un campo que no está permitido"""
    
class VolumenInvalidoError(Exception):
    """Se lanza cuando el volumen tiene in valor invalido"""
