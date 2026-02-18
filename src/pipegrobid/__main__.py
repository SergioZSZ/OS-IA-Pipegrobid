#funciones 
from .flow import grobid_request
from .flow import process_xml
from .flow import keyword_gen, figures_gen
from .flow import gen_txt
from .flow.auxiliar.dw_stopwords import dw_stopwords

#keyword cloud y visualizacion
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import requests

#flujo del proyecto

def main():
    '''
    PREVIA: envío de peticion get a GROBID para ver si está activo
    '''
    active = False
    try:
        response = requests.get("http://localhost:8070/api/isalive", timeout=5)
        active = True
    except requests.exceptions.RequestException:
        print("ERROR: No se pudo conectar a GROBID, verifique si está en ejecución.")

    if active == True:

            '''
            1er paso:

            mediante la función "grobid_request()" ealizamos las peticiones a grobid enviandole como input nuestros pdfs ubicados
            en la carpeta 'pdfs' enviándoselos directamente mediante request, guardando
            su respuesta (los .tei.xml) en la carpeta 'xmls'
            Si devuelve 1 el metodo significa que no hay pdfs en la carpeta, por lo que no se ejecuta
            nada mas hasta que el usuario los meta, si devuelve 0 continuamos
            '''

            response = grobid_request()
            if response == 0:

                '''
                2º paso:

                Una vez procesados los pdfs y generados los .tei.xml, la siguiente funcion 
                "process_xml()" se encargará de procesar los archivos con el formato dicho
                de la carpeta "xmls" y devolverá un dict con 4 valores:
                
                    -   xmls: lista de los nombres e los xmls ordenada 
                    -   abstracts: una lista con los abstracts sin stopwords, tokenizados y lematizados
                                    de todos los tei.xml procesados               
                    -   nfigures:  una lista con el nº de figuras encontradas en cada xml (ordenada)
                    .   links_per_paper: una lista con los links del propio paper
                    
                Si la funcion devuelve 1 significa que no había xml por lo que no sigue el flujo
                
                NOTA: para poder acceder a las stopwords de un lenguaje es necesario descargarse 1 vez:
                        nltk.download("stopwords")
                        nltk.download("wordnet")
                        nltk.download("omw-1.4")
                        se descargan mediante la funcion declarada en dw_stopwords.py, solo descargandose
                        la primera vez que se usa esa funcion, el resto no
                
                '''
                dw_stopwords()
                xmls_abstracts_figures_links = process_xml()
                if xmls_abstracts_figures_links != 1:
                    
                    '''
                    3er paso:
                    
                    unimos todos los abstracts en un unico texto que le pasaremos a "keyword_gen(text)"
                    para generar a partir del texto y guardar un png que es  el keyword cloud 
                    y generaremos otro png con el nº de palabras que salen a partir de los nombres
                    de los xmls y del nº de figuras mediante "figures_gen"
                    '''
                    
                    text = " ".join(xmls_abstracts_figures_links.get("abstracts"))
                    keyword_gen(text)
                    
                    
                    papers = xmls_abstracts_figures_links.get("xmls")
                    counts = xmls_abstracts_figures_links.get("nfigures")
                        
                    figures_gen(papers,counts)
                    
                    '''
                    4º paso:
                    
                    generamos un txt con todos los links por paper mediante la funcion "gen_txt"
                    '''
                    links_per_paper = xmls_abstracts_figures_links.get("links_per_paper")
                    
                    gen_txt(links_per_paper)
                    
                    
if __name__ == "__main__":
    main()          
