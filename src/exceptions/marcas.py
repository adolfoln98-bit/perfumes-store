class MarcaDuplicadaError(Exception):
    """Se lanza cuando se intenta crear una marca existente."""
    
class MarcaNoEncontradaError(Exception):
    """Se lanza cuando no se encuentra ninguna marca en la busqueda realizada."""

class MarcaIdInvalidaError(Exception):
    """Se lanca cuando el id de la marca es invalido"""