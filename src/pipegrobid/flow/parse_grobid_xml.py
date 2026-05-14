from pathlib import Path
import json
import xml.etree.ElementTree as et
from natsort import natsorted
import os
from auxiliar import parse_acknowledgements, parse_paper, parse_people

# Namespace de TEI.
# Los XML generados por GROBID usan este namespace, por eso hay que usarlo
# en las búsquedas XPath.
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

ROOT_DIR = Path(__file__).resolve().parents[3]


global count

    

# crea el json y le hace dump
def create_json(paper: dict, people: dict, acknowledgements: dict):


    # Carpeta de salida.
    output_dir = ROOT_DIR / "outputs" / "parsed_xmls"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_parse = {
        "paper": paper,
        "people": people,
        "organizations": [],
        "countries": [],
        "topics": [],
        "acknowledgements": acknowledgements
    }
    
    count +=1
    output_file = output_dir / f"paper_{count}.json"
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(json_parse, f, indent=2, ensure_ascii=False)
        



    

# parseo de un solo paper
def parse_xml(xml_path):
    tree = et.parse(xml_path)
    root = tree.getroot()

    bibl = root.find(".//tei:sourceDesc/tei:biblStruct", NS)

    paper = parse_paper(root,xml_path)
    people = parse_people(bibl)
    acknowledgements = parse_acknowledgements(root)

    return create_json(
        paper=paper,
        people=people,
        acknowledgements=acknowledgements
    )
    
    
    
    
    
# parseo de todos los xmls
def parse_all():
    xmls_dir = ROOT_DIR / "outputs" / "xmls"
    
    # Comprobamos que la carpeta exista
    if not os.path.exists(xmls_dir):
        raise FileNotFoundError(f"ERROR: No existe la carpeta de XMLs: {xmls_dir}")

    # Buscamos solo ficheros que acaben en .tei.xml
    xml_files = [
        file_name
        for file_name in os.listdir(xmls_dir)
        if file_name.endswith(".tei.xml")
    ]

    # Orden natural: paper1, paper2, paper3, ..., paper10
    xml_files = natsorted(xml_files)

    # Si no hay XMLs, paramos el programa con error
    if not xml_files:
        raise FileNotFoundError(f"ERROR: No se encontraron XMLs .tei.xml en: {xmls_dir}")
        
    
    generated_jsons = []

    # Procesamos los XML uno a uno
    for xml_file in xml_files:
        xml_path = xmls_dir / xml_file

        print(f"Parseando {xml_file}...")

        output_json = parse_xml(xml_path)

        generated_jsons.append(output_json)

    print(f"\nProcesados {len(generated_jsons)} XML correctamente.")

    return generated_jsons


if __name__ == "__main__":
    parse_all()