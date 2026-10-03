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

class FiltroPrecioInvalidoError(Exception):
    """Se lanza cuando el valor del filtro de precio minimo es mayor el valor de precio maximo"""

class CriterioDeOrdenacionInvalidaError(Exception):
    """Se lanza cuando se usa un filtro de busqueda invalido"""

class DireccionDeOrdenacionInvalidaError(Exception):
    """Se lanza cuando la direccion de ordenacion no es valida"""

class DescuentoInvalidoError(Exception):
    """Se lanza cuando el descuento introducido es mayor a 100 o menor a 0"""