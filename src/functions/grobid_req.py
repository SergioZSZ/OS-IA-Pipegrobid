import requests # libreria que usaremos para realizar peticiones a la API de grobid 
import os,sys

# dir del directorio base
BASE_DIR = os.path.join(os.path.dirname(__file__),"..","..")
#directorios de pdfs y de xmls
PDFS_DIR = os.path.join(BASE_DIR,"pdfs")
XMLS_DIR = os.path.join(BASE_DIR,"xmls")


def grobid_request():
    print(PDFS_DIR)
    print("\n************** GROBID REQUEST **************")
    
    # url de la API que usaremos
    url_process_document = "http://localhost:8070/api/processFulltextDocument"

    
    ########### preparacion del entorno y seleccion de pdfs
    print("Generando/Validando entorno...\n")
    
    os.makedirs(PDFS_DIR, exist_ok=True)
    os.makedirs(XMLS_DIR, exist_ok=True)

    print("Seleccionando archivos:")

    # solo metemos pdfs en el array de la carpeta pdfs
    pdfs = []
    for pdf in os.listdir(PDFS_DIR):  
        if pdf.endswith(".pdf"):
            
            pdf_path = os.path.join(PDFS_DIR,pdf) 
            pdfs.append(pdf_path)
            print(f"    {pdf}")   

    # si no hay pdfs warning al usuario y terminamos la ejecucion
    if not pdfs:
        print(f"WARNING: Ningún PDF en la carpeta '{PDFS_DIR}', por favor, introduzcalos")
        return 1






    ################ peticiones a grobid
    tam_pdfs = len(pdfs)

    print(f"\nIniciando request a GROBID ({tam_pdfs} .pdf):")
    for i, pdf in enumerate(pdfs):
        
        try:
            with open(pdf,"rb") as file:    # archivos pdf se abren en modo binario
                send = {"input": file}    # se espera que el parametro de entrada se llame input + archivo
                response = requests.post(url_process_document, files=send)
            
        # posibles excepciones de request o abrir el archivo
        except Exception as e:
            print(f"ERROR: error procesando {pdf}: {e}")
            continue

        # logs de la request y su codigo de respuesta
        print(f"    request {i+1}/{tam_pdfs} reponse_cod:{response.status_code}")


        # si se procesa bien la peticion lo escriba en un tei.xml
        if response.status_code == 200:
            path_xml = f"{XMLS_DIR}/paper{i+1}.tei.xml"
            
            with open(path_xml,"w", encoding= "utf-8") as paper:
                paper.write(response.text)



    print("\nFIN: Request Finalizados.\n")
    return 0

            
            