from .auxiliar.clean_text import clean_text
import os, re

from natsort import natsorted # organiza strings de manera natural (paper1,paper2,paper3 ...)
import xml.etree.ElementTree as et #extraccion de partes de un xml como si fuese un arbol


#sin este namespace no SE encuentran los nodos del xml debido al formato TEI
NS = {"tei": "http://www.tei-c.org/ns/1.0"} 


# encapsulamiento en una lista las direcciones de los xmls del directorio dado
def list_xmls(xmls_dir: str) -> list:
    xmls = []
    for xml in os.listdir(xmls_dir):
        if xml.endswith(".tei.xml"): 
            path = os.path.join(xmls_dir,xml) 
            xmls.append(path)  
            print(f"    {xml}")
    return xmls



# búsqueda de links en un xml (nodos ptr y texto)
def links_research(ptrs: list[et.Element] , root: et.Element) -> list:
    links = []  
    for el in ptrs:              
        target = el.get("target")
        if target and target.startswith("http"):
            links.append(target)
        
    for el in root.iter():
        if el.text:
            lista = re.findall(r"https?://[^\s\"<>()]+", el.text)
            for link in lista:
                links.append(link)
    return links






# extraccion de datos del xml 
def extract_data(xml: str, abstracts: list[str], figures_count: list[int], links_per_paper: dict) -> None:
    tree = et.parse(xml)    # parseamos en arbol el xml
    root = tree.getroot()   # sacamos el nodo raiz desde el que trabajamos
        
    abstract = root.find(".//tei:abstract",NS) # buscamos desde el nodo root a cualquier profundidad abstract
    figures = root.findall(".//tei:figure",NS) # buscamos todas las figuras
    ptrs = root.findall(".//tei:ptr",NS)       # en ptr hay links(en texto mas adelante)
        
    if abstract is not None:
        text = " ".join(abstract.itertext()) # recorre los nodos hijos de abstract para unirlo con ""
        text = re.sub(r"\s+", " ", text).strip() # elimina espacios extras seguidos por uno solo
        abstracts.append(text)
    
    n_figures = len(figures)
    figures_count.append(n_figures)  # añadimos el nº de figuras que hay
    
    # busqueda de links
    links_per_paper[xml] = links_research(ptrs, root)






'''
flujo:
    1º listado de .tei.xmls y ordenación, si no hay se termina el flujo
    2º extraccion de abstracts, figures, links 
    3º limpieza de abstracts
    4º devolver diccionario {xmls, abstracts, figures, links}
'''
def process_xml(xmls_dir: str) -> dict:
    res = {}
    res["error"]= False
    # si no hay xmls warning al usuario y terminamos la ejecucion
    
    print("\n.tei.xmls a procesar:")
    xmls = list_xmls(xmls_dir)
    print("\n")
    
    if not xmls:
        res["error"]= True
        return res    

    # ordenamos de menor a mayor los xmls
    xmls = natsorted(xmls)
    
    # extraccion de datos del xml
    abstracts = []
    figures_count = []
    links_per_paper = {}
    
    # extraccion de abstracts, nº figuras, links 
    for i,xml in enumerate(xmls):    
        extract_data(xml, abstracts, figures_count, links_per_paper)

    # limpieza de abstracts
    cleaned_abstracts = []
    for i,abstract in enumerate(abstracts):
        cleaned_abstracts.append(clean_text(abstract))


    res["xmls"] = xmls
    res["abstracts"] = cleaned_abstracts
    res["nfigures"] = figures_count
    res["links_per_paper"] = links_per_paper
    
    return res
    

        

        

        
        

