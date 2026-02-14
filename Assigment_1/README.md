# Assigment 1: Procesamiento de documentos científicos mediante el software GROBID

## Estructura del proyecto
```
Assigment_1/
│
├── .venv/                      # Entorno virtual (lo tienes que generar)
│
├── functions/                  # Modulos y funciones usados en el programa
│   ├── __init__.py
│   ├── clean_text.py           # Procesamiento de texto 
│   ├── dw_stopwords.py         # Gestión de Stopwords y Lemmatizer 
│   ├── gen_pgns.py             # Generación de pngs (Keyword Cloud y Figures visualization) 
│   ├── gen_txt.py              # Generación del txt de links
│   ├── grobid_req.py           # GROBID API requests
│   └── process_xml.py          # Procesamiento de los ficheros .tei.xml
│
├── generated_files/                # Archivos generados tras ejecutar
│   ├── figures_visualization.png   
│   ├── keyword_cloud.png
│   └── links_per_paper.txt
│
├── pdfs/                       # Input de PDFs (meterlos aquí)
│
├── xmls/                       # Archivos XML generados (por GROBID)
│
├── main.py                     # Main del proyecto
├── README.md                   # Documentación
└── requirements.txt            # Dependencias de Python
```

## Descripción

Este proyecto consiste en la elaboración de un Pipe entre la API del software `GROBID` y el programa realizado para construir un Keyword Cloud, una gráfica de las figuras encontradas y los links de cada archivo `.pdf` que se le ofrezca al programa.

### Parte 1: Procesamiento de PDFs a formato .tei.xml mediante GROBID

Con GROBID ejecutado, mediante la función `grobid_req()` encontrada el script `/Assigment_1/functions/grobid_req.py`se le enviarán mediante peticiones request todos los `.pdf` encontrados en el directorio `/Assigment_1/pdfs` para su procesamiento y recibir en el directorio `/Assigment_1/xmls` la conversión de dichos archivos a formato `.tei.xml`, el cual es legible por máquinas para futuros procesamientos. 

- Si GROBID no está ejecutado en su máquina saltará un aviso y no se ejecutará el programa.
- El programa solo aceptará archivos en formato `.pdf` y que se encuentren en el directorio mencionado. 
- Si no se encuentran archivos `.pdf` se interrumpirá el programa saltando un aviso.
- En caso de no existir el directorio `/Assigment_1/pdfs` se creará automáticamente en la ejecución del Script y saltará el aviso dicho en el punto anterior.

### Parte 2: Extracción de abstracts, figures y links de los archivos .tei.xml

Antes de realizar la extraccion, se ejecuta la función `dw_stopwords()` del Script `/Assigment_1/functions/dw_stopwords.py`, la cual se encarga de descargar en el equipo (si no se ha descargado anteriormente) los paquetes necesarios para usar un lematizador de palabras y las stopwords de los idiomas (palabras muy concurrentes pero que no dan información util, como articulos o preposiciones), ya que este procesamiento es muy util para encontrar patrones y palabras clave para el entrenamiento de modelos o procesamiento de texto.

Mediante la función `process_xml()` encontrada en el script `/Assigment_1/functions/process_xml.py` se seleccionan todos todos los archivos `.tei.xml` del directorio `/Assigment_1/xmls` y se ordenan de manera natural gracias a la función externa `natsorted` de la librería `natsort`. Posteriormente se recorrerán las etiquetas de los archivos como nodos gracias a la librería de Python `xml.etree.ElementTree` extrayendo
- De los nodos abstract: El texto de todos los archivos para elaborar un Keyword Cloud.
- De los nodos figure: El nº de figuras que se encuentran en cada archivo.
- De los nodos ref y ptr: los links de los ficheros (encontrados en esos nodos) para generar un `.txt` diciendo en qué fichero se encuentran

El texto extraído de los abstracts posteriormente es procesado con una función implementada llamada `clean_text(text)` que acaba limpiando el texto para eliminar de el URLs, etiquetas XML, stopwords y lematiza las palabras restantes para facilitar su procesamiento a su vez que las tokenifica.

Debido a la manera que han sido ordenados los archivos, las listas donde se guardan las extracciones coinciden con la posición del archivo `.tei.xml` al que pertenecen.

Este Script acaba generando un diccionario con 4 elementos que recibirá el `main.py`:
'''
            "xmls": xmls,                   # lista con los nombres de los archivos ordenados
            "abstracts":cleaned_abstracts,  # lista con los abstracts tokenizados por archivo
            "nfigures":figures_count,       # nº de figuras encontradas por archivo
            "links_per_paper": links_per_paper  # links encontrado por archivo
'''
- Si no se encuentran archivos `.tei.xml` en el directorio `/Assigment_1/xmls` saltará un aviso y se terminará la ejecución del programa.
- Si no existe el directorio `/Assigment_1/xmls` se creará al ejecutar el Script, pero saltará el aviso anterior
- El programa solo aceptará archivos en formato `.tei.xml` y que se encuentren en el directorio mencionado. 

### Parte 3: Generación del Keyword Cloud, Visualización de nº de figuras y links.txt

Tras recibir el Script `main.py` el diccionario mencionado anteriormente usará los datos contenidos para usarlos en las siguientes funciones:

- Script ``/Assigment_1/functions/gen_pgns.py`:
    - `keyword_gen(text)`: Generar el keyword cloud en una imagen `keyword_cloud.png` mediante la librería `matplotlib` siendo `text` un string con todo el texto guardado en `cleaned_abstracts`
    - `figures_gen(papers, counts)`: Generar una imagen `figures_visualization.png` mediante la librería `matplotlib` usando `papers` como los nombres de los papers contenidos en la variable del diccionario `xmls` y siendo `counts` los valores de `nfigures` del diccionario

- Script `/Assigment_1/functions/gen_txt.py`:
    - `gen_txt(links_dict):` Generar el `.txt` indicando los links encontrados en `links_dict`cuyo valor es el de la variable del diccionario `links_per_paper` organizándolos por el paper al que corresponden


## Requisitos

- Docker y Docker Desktop
- Python 3.13.2
- Software GROBID (link mas adelante)
- Dependencias de Python usadas:

    -   `requests`: realización de peticiones a APIs
    -   `wordcloud`:    creación del wordcloud
    -   `matplotlib`:   generación y visualización de imágenes (wordcloud y figuras)
    -   `natsort`:  ordenación natural de strings 
    -   `nltk`: procesamiento del lenguaje natural(stopwords, lemmatizer)

## Instrucciones de instalación y preparación del entorno:

Se recomienda la creación de un entorno virtual en Python para la instalación de dependencias. Se puede crear en la carpeta raíz `/Assigment_1` mediante el mandato `python -m venv nombre_del_entorno` y se debe activar para instalar las dependencias y usarlas.
El entorno se activa diferente dependiendo del Sistema Operativo usado:
    -   Linux: `nombre_del_entorno/bin/activate`
    -   Windows: `nombre_del_entorno/Scripts/activate`

las dependencias pueden instalarse automáticamente mediante el archivo `requirements.txt` con el mandato `pip install -r requirements.txt`

Orden de instalación para ejecutar el proyecto:
- Instalar Docker: https://www.docker.com/
- Instalar GROBID, todo lo necesario para instalar se encuentra en https://github.com/grobidOrg/grobid
- Creación del entorno virtual desde `Assigment_1` con `python -m venv nombre_del_entorno`
- Activar el entorno (mencionado anteriormente) e instalar dependencias con `pip install -r requirements.txt`, sin el entorno activado se instalará en la máquina en vez de en él.

