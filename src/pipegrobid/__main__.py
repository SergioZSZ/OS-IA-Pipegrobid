# paquetes internos y modulos
from .flow import grobid_request                        # grobid_interaction.py
from .flow import process_xml                           # xml_processing.py
from .flow import keyword_gen, figures_gen, gen_txt     # generations.py

from .flow.auxiliar import dw_stopwords                 # dw_sopwords.py
from .flow.auxiliar import is_active_api                # isactive.py
from .flow.auxiliar import gen_env                      # environment.py
#peticiones a api grobid
import requests, os


# Directorios base
BASE_DIR = os.path.join(os.path.dirname(__file__),"..","..")

#direcciones de la api

# grobid base dependiendo se si dockerizado o lanzado en localhost
GROBID_BASE =  os.getenv("GROBID_URL","http://localhost:8070")
URL_ISACTIVE = f"{GROBID_BASE}/api/isalive"
URL_PROCESS_DOCS = f"{GROBID_BASE}/api/processFulltextDocument"

def main():
    
    print("Generando entorno...")
    # generación del entorno    
    dirs = gen_env(BASE_DIR)
    
    print("Comprobando si Grobid activo...")
    # envío de peticion get a GROBID para ver si está activo
    if not is_active_api(URL_ISACTIVE):
        print("ERROR: No se pudo conectar a GROBID, verifique si está en ejecución.")
        return
    else:
            #  envío de pdfs a grobid y generación de xmls
            error = grobid_request(dirs["pdfs"], dirs["xmls"], URL_PROCESS_DOCS)
            if error:
                print(f"WARNING: Ningún PDF en la carpeta 'pdfs', por favor, introduzcalos")
                return
            else:

                # descarga de stopwords y lemmatizer en caso de no tenerlo ya
                print("\nComprobando stopwords y lemmatizers...\n")
                dw_stopwords()
                
                # extraccion de nombres de xmls, abstracts, nºfiguras y links de los xmls
                xmls_abstracts_figures_links = process_xml(dirs["xmls"])
                
                if xmls_abstracts_figures_links["error"]:
                    print(f"WARNING: Ningún tei.xml en la carpeta 'xmls', por favor, genérelos mediante GROBID.")
                    return
                else:
                    # juntar en un unico texto los abstracts y generar el keyword cloud
                    text = " ".join(xmls_abstracts_figures_links.get("abstracts"))
                    keyword_gen(text,dirs["files"])
                    
                    # generación de una gráfica paper-nº figuras
                    papers = xmls_abstracts_figures_links.get("xmls")
                    counts = xmls_abstracts_figures_links.get("nfigures")
                        
                    figures_gen(papers,counts,dirs["files"])
                    
                    # generación .txt con links por cada paper
                    links_per_paper = xmls_abstracts_figures_links.get("links_per_paper")
                    gen_txt(links_per_paper,dirs["files"])
                    


# declaracion de que el main se ejecute al llamar al paquete pipegrobid                    
if __name__ == "__main__":
    main()          
