from .clean_text import clean_text
import os

from natsort import natsorted # organiza strings de manera natural (paper1,paper2,paper3 ...)
import xml.etree.ElementTree as et #extraccion de partes de un xml como si fuese un arbol


def process_xml():
    
    print("\n************** XML PROCESS **************")

    ##################### seleccion de xmls

    print("Seleccionando archivos xml:")

    xmls = []
    for xml in os.listdir("xmls"):
        if xml.endswith(".tei.xml"): #solo metemos los archivos .tei.xml
            
            path = os.path.join("xmls",xml) 
            xmls.append(path)  
            print(f"    {xml}")
    # si no hay pdfs warning al usuario y terminamos la ejecucion
    if not xmls:
        print(f"WARNING: Ningún tei.xml en la carpeta '{os.path.abspath('xmls')}', por favor, genérelos mediante GROBID.")
        return 1    


    #ordenamos de menor a mayor
    xmls = natsorted(xmls)
    ################## extraccion de la parte abstract de los xml
    print("\nExtrayendo abstracts, figuras y links de los documentos...")
    abstracts = []
    figures_count = []
    links_per_paper = {}
    
    ns = {"tei": "http://www.tei-c.org/ns/1.0"} #sin este namespace no encuentra el nodo debido al formato TEI

    for xml in xmls:    
        tree = et.parse(xml)    #parseamos en arbol el xml
        root = tree.getroot()   #sacamos el nodo raiz desde el que trabajamos
        
        abstract = root.find(".//tei:abstract",ns) #buscamos desde el nodo root a cualquier profundidad abstract
        figures = root.findall(".//tei:figure",ns) #buscamos todas las figuras
        refs = root.findall(".//tei:ref", ns)      #buscamos las referencias(links)
        ptrs = root.findall(".//tei:ptr",ns)       #en ptr hay mas links
        if abstract is not None:
            text = " ".join(abstract.itertext()) #recorre los nodos hijos de abstract para unirlo con ""
            abstracts.append(text)
        
        figures_count.append(len(figures))  #añadimos el nº de figuras que hay
        
        links = []
        for ref in refs:                #buscamos en las refs encontradas(en sus target) las url
            target = ref.get("target")
            if target and target.startswith("http"):
                links.append(target)
        
        
        for ptr in root.findall(".//tei:ptr", ns):  #lo mismo para las etiquetas ptr
            target = ptr.get("target")
            if target and target.startswith("http"):
                links.append(target)


        links_per_paper[xml] = links
        
        
    ################limpieza del abstract/tokenizacion/lemm
    print("\nLimpiando abstracts...")

    cleaned_abstracts = []
    for abstract in abstracts:
        cleaned_abstracts.append(clean_text(abstract))


    ## hacemos return de xmls y nfigures para la visualización de figuras y abstrats para el wordcloud
    return {
            "xmls": xmls,
            "abstracts":cleaned_abstracts,
            "nfigures":figures_count,
            "links_per_paper": links_per_paper
    }

        

        

        
        

