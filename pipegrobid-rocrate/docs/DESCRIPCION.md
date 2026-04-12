## Descripción

Este proyecto consiste en la elaboración de un Pipe entre la API del software `GROBID` y el programa realizado para construir un Keyword Cloud, una gráfica de las figuras encontradas y los links de cada archivo `.pdf` que se le ofrezca al programa. Mediante la ejecución del paquete `pipegrobid` desde el entorno creado del paquete, el cual llama a las funciones necesarias de los módulos codificados. 

Se usarán 2 endpoints de GROBID para el procedimiento
-   ``http://localhost:8070/api/isactive`` para verificar que está GROBID ejecutado
-   ``http://localhost:8070/api/processFulltextDocument`` para la extracción de los .pdfs


### Parte 1: Procesamiento de PDFs a formato .tei.xml mediante GROBID
- Módulo principal: `/src/pipegrobid/flow/grobid_interaction.py`

- Descripción:
    Con GROBID ejecutado, mediante la ejecución de `pipegrobid`, mediante `grobid_request(dir_pdfs: str, dir_xmls: str, url_process_docs: str) -> bool` del módulo se le enviarán mediante peticiones request todos los `.pdf` encontrados en el directorio `/pdfs` para su procesamiento y recibir en el directorio `/xmls` la conversión de dichos archivos a formato `.tei.xml`, el cual es legible por máquinas para futuros procesamientos. 

- Funciones del módulo
    - `list_pdfs(dir_pdfs: str)-> list`:
    devuelve la lista de .pdf del directorio dado
    - `request_post(pdf: str, url_process_docs: str) -> requests.Response`:
     realiza una petición a GROBID enviándole un .pdf y obteniendo la respuesta(en caso de acierto con el texto procesado en .tei.xml)
    - `write_xml(response: requests.Response, dir_xmls: str, i: int) -> None`:
     escribe y guarda  en el directorio dado el texto de la respuesta de GROBID en un archivo formato paper{i+1}.tei.xml
    - `grobid_request(dir_pdfs: str, dir_xmls: str, url_process_docs: str) -> bool`:
    Viene definido el flujo principal del módulo, devolviendo True si se pudo resolver todo sin problemas o False si se encontraron (que no haya pdfs en el directorio `/pdfs`)

#### Notas a tener en cuenta
- Si GROBID no está ejecutado en su máquina saltará un aviso y no se ejecutará el programa.
- El programa solo aceptará archivos en formato `.pdf` y que se encuentren en el directorio mencionado. 
- Si no se encuentran archivos `.pdf` se interrumpirá el programa saltando un aviso.
- En caso de no existir el directorio `/pdfs` se creará automáticamente en la ejecución del Script y saltará el aviso dicho en el punto anterior

### Parte 2: Extracción de abstracts, figures y links de los archivos .tei.xml

Antes de realizar la extraccion, se ejecuta la función `/dw_stopwords()` del módulo `/src/pipegrobid/flow/auxiliar/dw_stopwords.py`, la cual se encarga de descargar en el equipo (si no se ha descargado anteriormente) los paquetes necesarios para usar un lematizador de palabras y las stopwords de los idiomas (palabras muy concurrentes pero que no dan información util, como articulos o preposiciones), ya que este procesamiento es muy util para encontrar patrones y palabras clave para el entrenamiento de modelos o procesamiento de texto.

- Módulo principal `/src/pipegrobid/flow/xml_processing.py`

Se seleccionan todos los archivos `.tei.xml` del directorio `/xmls` y se ordenan de manera natural. Posteriormente se recorrerán las etiquetas de los archivos como nodos gracias a la librería de Python `xml.etree.ElementTree` extrayendo
- De los nodos abstract: El texto de todos los archivos para elaborar un Keyword Cloud.
- De los nodos figure: El nº de figuras que se encuentran en cada archivo.
- De los nodos ptr y del texto del xml: los links de los ficheros (encontrados en esos nodos) para generar un `.txt` diciendo en qué fichero se encuentran

El texto extraído de los abstracts posteriormente es procesado con una función implementada llamada `clean_text(text)` ubicada en el módulo `/src/pipegrobid/flow/auxiliar/clean_text.py` que acaba limpiando el texto para eliminar de el URLs, etiquetas XML, stopwords y lematiza las palabras restantes para facilitar su procesamiento a su vez que las tokenifica.

Debido a la manera que han sido ordenados los archivos, las listas donde se guardan las extracciones coinciden con la posición del archivo `.tei.xml` al que pertenecen.

Este Script acaba generando un diccionario con 4 elementos que recibirá el `__main__.py`:
{
            "xmls": xmls,                   # lista con los nombres de los archivos ordenados
            "abstracts":cleaned_abstracts,  # lista con los abstracts tokenizados por archivo
            "nfigures":figures_count,       # nº de figuras encontradas por archivo
            "links_per_paper": links_per_paper  # links encontrado por archivo
}
- Funciones:
    - `list_xmls(xmls_dir: str) -> list:`:
    Devuelve una lista ordenada naturalmente gracias a `natsort` de los `.tei.xml` del directorio `/xmls`
    - `links_research(ptrs: list[et.Element] , root: et.Element) -> list`:
    Devuelve una lista con los links encontrados tanto en los nodos <ptr> dados del archivo `.tei.xml` correspondiente como en el texto del fichero
    - `extract_data(xml: str, abstracts: list[str], figures_count: list[int], links_per_paper: dict) -> None`:
    Añade a la lista de abstracs, lista de nº de figuras y diccionario de links per paper las extracciones realizadas en los .tei.xml
    - `process_xml(xmls_dir: str) -> dict`:
    Contiene el flujo del módulo, haciendo que se ejecute en orden y devuelva un diccionario con 5 parámetros(abstracts, xmls, figures_count, links_per_paper, error).


- Notas:
    - Si no se encuentran archivos `.tei.xml` en el directorio `/xmls` saltará un aviso y se terminará la ejecución del programa.
    - Si no existe el directorio `/xmls` se creará al ejecutar el Script, pero saltará el aviso anterior
    - El programa solo aceptará archivos en formato `.tei.xml` y que se encuentren en el directorio mencionado. 

### Parte 3: Generación del Keyword Cloud, Visualización de nº de figuras y links.txt

Tras recibir el Script `main.py` el diccionario mencionado anteriormente usará los datos contenidos para usarlos en las siguientes funciones del módulo `/src/pipegrobid/flow/generations.py`:

- `keyword_gen(text)`: Generar el keyword cloud en una imagen `keyword_cloud.png` mediante la librería `matplotlib` siendo `text` un string con todo el texto guardado en `cleaned_abstracts`

- `figures_gen(papers, counts)`: Generar una imagen `figures_visualization.png` mediante la librería `matplotlib` usando `papers` como los nombres de los papers contenidos en la variable del diccionario `xmls` y siendo `counts` los valores de `nfigures` del diccionario

- `gen_txt(links_dict):` Generar el `.txt` indicando los links encontrados en `links_dict`cuyo valor es el de la variable del diccionario `links_per_paper` organizándolos por el paper al que corresponden
