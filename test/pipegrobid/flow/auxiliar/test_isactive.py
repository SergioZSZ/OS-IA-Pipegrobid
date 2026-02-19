import pytest

from pipegrobid.flow.auxiliar import is_active_api

URL_ISACTIVE = "http://localhost:8070/api/isalive"
URL_NOTACTIVE = "false uri"

def test_uri_no_activa():
    """
    Verificación de fallo al conectarse a una URL no activa
    devolviendo False
    """
    assert is_active_api(URL_NOTACTIVE) == False
    
    
def test_uri_activa():
    """
    Verificación de conexión a grobid estando este operativo
    """
    assert is_active_api(URL_NOTACTIVE) == False