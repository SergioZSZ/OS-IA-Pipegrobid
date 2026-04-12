import requests # libreria que usaremos para realizar peticiones a la API de grobid 
import os

# devolver una lista de los pdfs encontrados en el directorio dir_pdfs
def list_pdfs(dir_pdfs: str)-> list:

    pdfs = []
    for pdf in os.listdir(dir_pdfs):  
        if pdf.endswith(".pdf"):
            
            pdf_path = os.path.join(dir_pdfs, pdf) 
            pdfs.append(pdf_path)
            print(f"    {pdf}")   
            
    return pdfs





# request post a grobid y respuesta
def request_post(pdf: str, url_process_docs: str) -> requests.Response:
     with open(pdf,"rb") as file:    # archivo pdf se abren en modo binario
                send = {"input": file}    # se espera que el parametro de entrada se llame input + archivo
                return requests.post(url_process_docs, files=send)





# escribir los xml devueltos por grobid
def write_xml(response: requests.Response, dir_xmls: str, i: int) -> None:
            # si se procesa bien la peticion lo escriba en un tei.xml
        if response.status_code == 200:
            path_xml = f"{dir_xmls}/paper{i+1}.tei.xml"
            
            with open(path_xml,"w", encoding= "utf-8") as paper:
                paper.write(response.text)



'''
flujo:
    1º listamos pdfs del directorio dado, si no hay se termina la ejecución del programa
    2º realizamos posts a grobid de los pdfs para que nos devuelva los .tei.xml
    3º guardamos los .tei.xml en su respectivo directorio
    
    el paso 2 y 3 se realizan en un bucle procesando cada petición-respuesta
'''
def grobid_request(dir_pdfs: str, dir_xmls: str, url_process_docs: str) -> bool:    
    
    #1º
    print("\npreparando extracción de los .pdf:")
    pdfs = list_pdfs(dir_pdfs)
    print("\n")
    if not pdfs:
        return True

    #2º 
    tam_pdfs = len(pdfs)
    for i, pdf in enumerate(pdfs):
        try:
            response = request_post(pdf, url_process_docs)
            
        except Exception as e:
            print(f"ERROR: error procesando {pdf}: {e}")
            continue

        # logs request
        print(f"    request {i+1}/{tam_pdfs} reponse_cod: {response.status_code}")

        #3º
        write_xml(response, dir_xmls,i)
        
    return False

            
            