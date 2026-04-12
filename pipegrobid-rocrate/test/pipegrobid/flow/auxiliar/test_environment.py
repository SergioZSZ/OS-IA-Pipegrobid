import pytest

from pipegrobid.flow.auxiliar import gen_env

def test_generacion_de_entorno(tmp_path):
    """
    Verifica que gen_env crea correctamente la estructura
    de directorios esperada dentro de un directorio temporal.    
    """
    tmp_base_dir = tmp_path
    dirs = gen_env(tmp_base_dir)
    
    assert (tmp_base_dir / "pdfs").exists()
    assert (tmp_base_dir / "pdfs").is_dir()

    assert (tmp_base_dir / "xmls").exists()
    assert (tmp_base_dir / "xmls").is_dir()

    assert (tmp_base_dir / "generated_files").exists()
    assert (tmp_base_dir / "generated_files").is_dir()