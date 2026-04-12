import os, pytest
import xml.etree.ElementTree as et
from pipegrobid.flow.xml_processing import list_xmls, links_research, extract_data



# test de list_xmls
def test_list_xmls_empty(tmp_path):
    """
    Validación list_xmls: directorio vacío
    """
    result = list_xmls(str(tmp_path))
    assert result == []



def test_list_xmls_only_tei(tmp_path):
    """
    Validación list_xmls: solo devuelve archivos .tei.xml
    """
    xml1 = tmp_path / "paper1.tei.xml"
    xml2 = tmp_path / "paper2.tei.xml"
    other = tmp_path / "test.txt"

    xml1.touch()
    xml2.touch()
    other.touch()

    result = list_xmls(str(tmp_path))

    expected = {str(xml1), str(xml2)}
    assert set(result) == expected
    
    
    



# test de links_research
def test_links_research_ptr_and_text():
    """
    Validación links_research: extrae links de nodos ptr y del texto
    """

    xml_content = """
    <root xmlns="http://www.tei-c.org/ns/1.0">
        <ptr target="http://example.com"/>
        <p>Visit https://openai.com for info</p>
    </root>
    """

    root = et.fromstring(xml_content)

    NS = {"tei": "http://www.tei-c.org/ns/1.0"}
    ptrs = root.findall(".//tei:ptr", NS)

    links = links_research(ptrs, root)

    assert "http://example.com" in links
    assert "https://openai.com" in links
    assert len(links) == 2





# test de extract data
def test_extract_data(tmp_path):
    """
    Validación extract_data: extrae abstract, nº figuras y links correctamente
    """

    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <abstract>
            <p>This is a test abstract.</p>
        </abstract>
        <figure/>
        <figure/>
        <ptr target="http://example.com"/>
    </TEI>
    """

    xml_file = tmp_path / "paper1.tei.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    abstracts = []
    figures_count = []
    links_per_paper = {}


    extract_data(str(xml_file), abstracts, figures_count, links_per_paper)

    # abstract
    assert abstracts == ["This is a test abstract."]

    # figuras
    assert figures_count == [2]

    # links
    assert str(xml_file) in links_per_paper
    assert "http://example.com" in links_per_paper[str(xml_file)]
