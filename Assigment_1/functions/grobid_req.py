import requests # libreria que usaremos para realizar peticiones a la API de grobid 
import os,sys


def grobid_request():
    
    print("\n************** GROBID REQUEST **************")
    
    # url de la API que usaremos
    url_process_document = "http://localhost:8070/api/processFulltextDocument"

    ########### preparacion del entorno y seleccion de pdfs
    print("Generando/Validando entorno...\n")

    os.makedirs("pdfs",exist_ok=True)
    os.makedirs("xmls", exist_ok=True)

    print("Seleccionando archivos:")

    # solo metemos pdfs en el array de la carpeta pdfs
    pdfs = []
    for pdf in os.listdir("pdfs"):  
        if pdf.endswith(".pdf"):
            
            pdf_path = os.path.join("pdfs",pdf) 
            pdfs.append(pdf_path)
            print(f"    {pdf}")   

    # si no hay pdfs warning al usuario y terminamos la ejecucion
    if not pdfs:
        print(f"WARNING: Ningún PDF en la carpeta '{os.path.abspath('pdfs')}', por favor, introduzcalos")
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
            path_xml = f"xmls/paper{i+1}.tei.xml"
            
            with open(path_xml,"w", encoding= "utf-8") as paper:
                paper.write(response.text)



    print("\nFIN: Request Finalizados.\n")
    return 0

            
            