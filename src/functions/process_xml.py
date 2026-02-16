from .clean_text import clean_text
import os
import re

from natsort import natsorted # organiza strings de manera natural (paper1,paper2,paper3 ...)
import xml.etree.ElementTree as et #extraccion de partes de un xml como si fuese un arbol

#directorio base y xmls
BASE_DIR = os.path.join(os.path.dirname(__file__),"..","..")
XMLS_DIR = os.path.join(BASE_DIR,"xmls")

def process_xml():
    
    print("\n************** XML PROCESS **************")

    
    ##################### seleccion de xmls

    print("Seleccionando archivos xml:")

    xmls = []
    for xml in os.listdir(XMLS_DIR):
        if xml.endswith(".tei.xml"): #solo metemos los archivos .tei.xml
            
            path = os.path.join(XMLS_DIR,xml) 
            xmls.append(path)  
            print(f"    {xml}")
    # si no hay pdfs warning al usuario y terminamos la ejecucion
    if not xmls:
        print(f"WARNING: Ningún tei.xml en la carpeta '{XMLS_DIR}', por favor, genérelos mediante GROBID.")
        return 1    


    #ordenamos de menor a mayor
    xmls = natsorted(xmls)
    ################## extraccion de la parte abstract de los xml
    print("\nExtrayendo abstracts, figuras y links de los documentos...")
    abstracts = []
    figures_count = []
    links_per_paper = {}
    text: str
    
    ns = {"tei": "http://www.tei-c.org/ns/1.0"} #sin este namespace no encuentra el nodo debido al formato TEI

    for i, xml in enumerate(xmls):    
        tree = et.parse(xml)    #parseamos en arbol el xml
        root = tree.getroot()   #sacamos el nodo raiz desde el que trabajamos
        
        abstract = root.find(".//tei:abstract",ns) #buscamos desde el nodo root a cualquier profundidad abstract
        figures = root.findall(".//tei:figure",ns) #buscamos todas las figuras
        ptrs = root.findall(".//tei:ptr",ns)       #en ptr hay links(en texto mas adelante)
        
            
        if abstract is not None:
            text = " ".join(abstract.itertext()) #recorre los nodos hijos de abstract para unirlo con ""
            abstracts.append(text)
        
        figures_count.append(len(figures))  #añadimos el nº de figuras que hay
        
        links = []
        
        #buscamos links en todas las etiquetas en las que suele haber de un xml y en el texto
        for el in ptrs:              
            target = el.get("target")
            if target and target.startswith("http"):
                links.append(target)
        
        for el in root.iter():
            if el.text:
                lista = re.findall(r"https?://[^\s\"<>()]+", el.text)
                for link in lista:
                    links.append(link)






        links_per_paper[xml] = links

#        '''
#        PARTE 1
#        para validacion del paper1 (A Multi-Agent LLM Framework for Realistic Patient.pdf)
#        parte: abstract correspondiente al paper, nº figuras y links
#        '''
#        if i == 0:
#            print("***************************** VALIDACION ***************************** ")
#            print(f"\npaper: {xml} \n\nabstract: {abstracts[i]}\n\nnfigures: {figures_count[i]}\n\nlinks: {links_per_paper[xml]}")
#            print("\n\n\n")
#        '''
#        FIN PARTE 1
#        '''
        
        
    ################limpieza del abstract/tokenizacion/lemm
    print("\nLimpiando abstracts...")

    cleaned_abstracts = []
    for i, abstract in enumerate(abstracts):
        cleaned_abstracts.append(clean_text(abstract))
        
        
#        '''
#        PARTE 2
#        para validacion de limpieza del abstract, lematización etc
#        '''
#        if i == 0:
#            print(f"\ncleaned abstract: {cleaned_abstracts[i]}")
#            print("\n\n\n")
#            print("********************************************************** ")
#        '''
#        FIN PARTE 1
#        '''
        

    ## hacemos return de xmls y nfigures para la visualización de figuras y abstrats para el wordcloud
    return {
            "xmls": xmls,
            "abstracts":cleaned_abstracts,
            "nfigures":figures_count,
            "links_per_paper": links_per_paper
    }

        

        

        
        

