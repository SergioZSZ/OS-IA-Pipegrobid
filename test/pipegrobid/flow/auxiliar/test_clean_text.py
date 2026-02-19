from pipegrobid.flow.auxiliar.clean_text import clean_text
import pytest


def test_clean_text_lowercase():
    """
    Validación del procesado de texto: conversión de mayúsculas a minúsculas
    """
    text = "HoLa MuNdO"
    assert clean_text(text) == "hola mundo"


def test_clean_text_del_xml_labels():
    """
    Validación del procesado de texto: eliminación de etiquetas XML
    """
    text = "<abstract><p>Hello World</p></abstract>"
    assert clean_text(text) == "hello world"


def test_clean_text_del_urls():
    """
    Validación del procesado de texto: eliminación de URLs
    """
    text = "visit http://example.com "
    # "visit" y "now" son stopwords? no. Entonces se mantienen.
    assert clean_text(text) == "visit"


def test_clean_text_del_digits():
    """
    Validación del procesado de texto: eliminación de dígitos
    """
    text = "experiment 2024 results"
    assert clean_text(text) == "experiment result"


def test_clean_text_del_punctuation():
    """
    Validación del procesado de texto: eliminación de signos de puntuación
    """
    text = "hello, world!!!"
    assert clean_text(text) == "hello world"


def test_clean_text_remove_stopwords():
    """
    Validación del procesado de texto: eliminación de stopwords en inglés
    """
    text = "this is a simple test"
    # stopwords: this, is, a
    assert clean_text(text) == "simple test"


def test_clean_text_lemmatization():
    """
    Validación del procesado de texto: lematización de palabras
    """
    text = "cars running"
    # running → running (WordNetLemmatizer sin POS no cambia verbos)
    # cars → car
    assert clean_text(text) == "car running"
    
    
def test_clean_text_full_pipeline():
    """
    Validación integral del procesado de texto:
    minúsculas, eliminación de XML, URLs, números,
    puntuación, stopwords, lematización y normalización de espacios.
    """
    text = """
    <abstract>This is a TEST 2026!!! Visit http://example.com
    Cars running in the streets.</abstract>
    """

    result = clean_text(text)

    expected = "test visit car running street"

    assert result == expected

