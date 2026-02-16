[DOI: 10.5281/zenodo.18664377](https://doi.org/10.5281/zenodo.18664377)

# Software para procesamiento de documentos científicos mediante el software GROBID
## Objetivo del proyecto

El objetivo de este proyecto es construir un pipeline automatizado para:
- Procesar documentos científicos en formato PDF mediante GROBID
- Extraer información estructurada (abstract, figuras y enlaces)
- Aplicar técnicas básicas de NLP sobre los abstracts
- Generar visualizaciones y archivos resumen a partir de la información extraída

Para la realización del proyecto, se utiliza GROBID debido a que convierte documentos PDF científicos en formato TEI XML estructurado, lo cual permite realizar extracción automática de información mediante procesamiento de nodos

El flujo del proyecto es:

PDF -> GROBID -> TEI XML -> Extracción -> Limpieza NLP -> Visualización y TXT


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

Se recomienda la creación de un entorno virtual en Python para la instalación de dependencias, por organización se puede crear en el directorio del código `/src` mediante el mandato `python -m venv nombre_del_entorno` y se debe activar para instalar las dependencias y usarlas.
El entorno se activa diferente dependiendo del Sistema Operativo usado:
    -   Linux: `nombre_del_entorno/bin/activate`
    -   Windows: `nombre_del_entorno/Scripts/activate`

las dependencias pueden instalarse automáticamente mediante el archivo `requirements.txt` con el mandato `pip install -r requirements.txt` estando el entorno activo

Orden de instalación para ejecutar el proyecto:
- Instalar Docker: https://www.docker.com/
- Instalar GROBID, todo lo necesario para instalar se encuentra en https://github.com/grobidOrg/grobid
- Creación del entorno virtual desde `src` con `python -m venv nombre_del_entorno`
- Activar el entorno (mencionado anteriormente) e instalar dependencias con `pip install -r requirements.txt`, sin el entorno activado se instalará en la máquina en vez de en él

## Estructura del proyecto
```
/
├── generated_files/                # Archivos generados tras ejecutar
│   ├── figures_visualization.png   
│   ├── keyword_cloud.png
│   └── links_per_paper.txt
│
├── pdfs/                       # Input de PDFs (meterlos aquí)
│
├── xmls/                       # Archivos XML generados (por GROBID)
│
├── CITATION.cff                # Cómo citar el software 
│
├── LICENSE                     # Licencia del Software
│
├── README.md                   # Documentación         
│
├── requirements.txt            # Dependencias de Python a instalar
│
└── src/
    │
    ├── .venv/                      # Entorno virtual (lo tienes que generar)
    │
    ├── main.py                     # Main del proyecto
    │
    └── functions/                  # Modulos y funciones usados en el programa
       ├── __init__.py
       ├── clean_text.py           # Procesamiento de texto 
       ├── dw_stopwords.py         # Gestión de Stopwords y Lemmatizer 
       ├── gen_pgns.py             # Generación de pngs (Keyword Cloud y Figures visualization) 
       ├── gen_txt.py              # Generación del txt de links
       ├── grobid_req.py           # GROBID API requests
       └── process_xml.py          # Procesamiento de los ficheros .tei.xml
    


    
```

## Descripción

Este proyecto consiste en la elaboración de un Pipe entre la API del software `GROBID` y el programa realizado para construir un Keyword Cloud, una gráfica de las figuras encontradas y los links de cada archivo `.pdf` que se le ofrezca al programa. Mediante la ejecución del script `main.py` con el mandato `python main.py`, el cual llama a las funciones necesarias de los módulos codificados. 

### Parte 1: Procesamiento de PDFs a formato .tei.xml mediante GROBID

Con GROBID ejecutado, mediante la función `grobid_req()` encontrada el script `/src/functions/grobid_req.py`se le enviarán mediante peticiones request todos los `.pdf` encontrados en el directorio `/pdfs` para su procesamiento y recibir en el directorio `/xmls` la conversión de dichos archivos a formato `.tei.xml`, el cual es legible por máquinas para futuros procesamientos. 

- Si GROBID no está ejecutado en su máquina saltará un aviso y no se ejecutará el programa.
- El programa solo aceptará archivos en formato `.pdf` y que se encuentren en el directorio mencionado. 
- Si no se encuentran archivos `.pdf` se interrumpirá el programa saltando un aviso.
- En caso de no existir el directorio `/pdfs` se creará automáticamente en la ejecución del Script y saltará el aviso dicho en el punto anterior

### Parte 2: Extracción de abstracts, figures y links de los archivos .tei.xml

Antes de realizar la extraccion, se ejecuta la función `dw_stopwords()` del Script `/src/functions/dw_stopwords.py`, la cual se encarga de descargar en el equipo (si no se ha descargado anteriormente) los paquetes necesarios para usar un lematizador de palabras y las stopwords de los idiomas (palabras muy concurrentes pero que no dan información util, como articulos o preposiciones), ya que este procesamiento es muy util para encontrar patrones y palabras clave para el entrenamiento de modelos o procesamiento de texto.

Mediante la función `process_xml()` encontrada en el script `/src/functions/process_xml.py` se seleccionan todos todos los archivos `.tei.xml` del directorio `/xmls` y se ordenan de manera natural gracias a la función externa `natsorted` de la librería `natsort`. Posteriormente se recorrerán las etiquetas de los archivos como nodos gracias a la librería de Python `xml.etree.ElementTree` extrayendo
- De los nodos abstract: El texto de todos los archivos para elaborar un Keyword Cloud.
- De los nodos figure: El nº de figuras que se encuentran en cada archivo.
- De los nodos ref y ptr y del texto del xml: los links de los ficheros (encontrados en esos nodos) para generar un `.txt` diciendo en qué fichero se encuentran

El texto extraído de los abstracts posteriormente es procesado con una función implementada llamada `clean_text(text)` que acaba limpiando el texto para eliminar de el URLs, etiquetas XML, stopwords y lematiza las palabras restantes para facilitar su procesamiento a su vez que las tokenifica.

Debido a la manera que han sido ordenados los archivos, las listas donde se guardan las extracciones coinciden con la posición del archivo `.tei.xml` al que pertenecen.

Este Script acaba generando un diccionario con 4 elementos que recibirá el `main.py`:
'''
            "xmls": xmls,                   # lista con los nombres de los archivos ordenados
            "abstracts":cleaned_abstracts,  # lista con los abstracts tokenizados por archivo
            "nfigures":figures_count,       # nº de figuras encontradas por archivo
            "links_per_paper": links_per_paper  # links encontrado por archivo
'''
- Si no se encuentran archivos `.tei.xml` en el directorio `/xmls` saltará un aviso y se terminará la ejecución del programa.
- Si no existe el directorio `/xmls` se creará al ejecutar el Script, pero saltará el aviso anterior
- El programa solo aceptará archivos en formato `.tei.xml` y que se encuentren en el directorio mencionado. 

### Parte 3: Generación del Keyword Cloud, Visualización de nº de figuras y links.txt

Tras recibir el Script `main.py` el diccionario mencionado anteriormente usará los datos contenidos para usarlos en las siguientes funciones:

- Script ``/src/functions/gen_pgns.py`:
    - `keyword_gen(text)`: Generar el keyword cloud en una imagen `keyword_cloud.png` mediante la librería `matplotlib` siendo `text` un string con todo el texto guardado en `cleaned_abstracts`
    - `figures_gen(papers, counts)`: Generar una imagen `figures_visualization.png` mediante la librería `matplotlib` usando `papers` como los nombres de los papers contenidos en la variable del diccionario `xmls` y siendo `counts` los valores de `nfigures` del diccionario

- Script `/src/functions/gen_txt.py`:
    - `gen_txt(links_dict):` Generar el `.txt` indicando los links encontrados en `links_dict`cuyo valor es el de la variable del diccionario `links_per_paper` organizándolos por el paper al que corresponden

## Validaciones

Para realizar las siguientes validaciones se usó el documento `.pdf` con ruta `/pdfs/A Multi-Agent LLM Framework for Realistic Patient.pdf`

### 1. Funcionamiento de GROBID

En el propio Script `/src/main.py` se codificó una peticion GET a la API de GROBID para verificar su funcionamiento con un timeout de 5 segundos. Pueden ocurrir 2 casos:
    - La petición GET devuelve un booleano `True` y se ejecuta el resto del código
    - La petición GET no recibe respuesta y salta un aviso de que no se pudo conectar a GROBID

### 2. Coherencia con la extracción de abstracts, nº figures y links
Para verificar la Coherencia de los datos extraídos, se añadieron en el Script `/src/functions/process_xml.py` en la funcion `process_xml()` dos bloques de código:

- 1º (líneas 71-82): Para el primer paper generado (correspondiente al pdf mencionado al principio de este bloque) se imprime por pantalla el nombre del paper, el abstract extraído, su número de figuras y links (posteriormente añadidas al diccionario que se envía a `/src/main.py`), Saliendo por pantalla:
```
***************************** VALIDACION ***************************** 

paper: xmls\paper1.tei.xml

abstract:
 Simulating high-fidelity patients offers a powerful avenue for studying complex diseases while addressing the challenges of fragmented, biased, and privacy-restricted real-world data. In this study, we introduce SynthAgent, a novel Multi-Agent System (MAS) framework designed to model obesity patients with comorbid mental disorders, including depression, anxiety, social phobia, and binge eating disorder. SynthAgent integrates clinical and medical evidence from claims data, population surveys, and patient-centered literature to construct personalized virtual patients enriched with personality traits that influence adherence, emotion regulation, and lifestyle behaviors. Through autonomous agent interactions, the system simulates disease progression, treatment response, and life management across diverse psychosocial contexts. Evaluation of more than 100 generated patients demonstrated that GPT-5 and Claude 4.5 Sonnet achieved the highest fidelity as the core engine in the proposed MAS framework, outperforming Gemini 2.5 Pro and DeepSeek-R1. SynthAgent thus provides a scalable and privacy-preserving framework for exploring patient journeys, behavioral dynamics, and decision-making processes in both medical and psychological domains.

nfigures: 6

links: ['https://github.com/kermitt2/grobid', 'https://wwwn.cdc.gov/nchs/nhanes/.Hyattsville', 'https://www.cdc.gov/brfss/index.htm', 'https://data.worldobesity.org/country/united-states-227/.GlobalObesityObservatory', 'https://openai.com/gpt-5/.Largelanguagemodel', 'https://www.anthropic.com/news/claude-sonnet-4-5.Largelanguagemodel', 'https://purplelab.com']
```

- 2º (líneas 100-109): se muestra por pantalla el abstract limpio y lematizado para ver qué palabras se repiten más, por pantalla muestra esa parte del código:
```
cleaned abstract: simulating high fidelity patient offer powerful avenue studying complex disease addressing challenge fragmented biased privacy restricted real world data study introduce synthagent novel multi agent system ma framework designed model obesity patient comorbid mental disorder including depression anxiety social phobia binge eating disorder synthagent integrates clinical medical evidence claim data population survey patient centered literature construct personalized virtual patient enriched personality trait influence adherence emotion regulation lifestyle behavior autonomous agent interaction system simulates disease progression treatment response life management across diverse psychosocial context evaluation generated patient demonstrated gpt claude sonnet achieved highest fidelity core engine proposed ma framework outperforming gemini pro deepseek r synthagent thus provides scalable privacy preserving framework exploring patient journey behavioral dynamic decision making process medical psychological domain




**********************************************************
```
#### Coherencia Abstract
Por pantalla se muestra el paper `xmls/paper1.tei.xml`
Yéndonos a las líneas 76-78 del paper correspondiente `/xmls/paper1.tei.xml` encontramos el abstract con el mismo texto que sale por pantalla:
```
			<abstract>
<div xmlns="http://www.tei-c.org/ns/1.0"><p>Simulating high-fidelity patients offers a powerful avenue for studying complex diseases while addressing the challenges of fragmented, biased, and privacy-restricted real-world data. In this study, we introduce SynthAgent, a novel Multi-Agent System (MAS) framework designed to model obesity patients with comorbid mental disorders, including depression, anxiety, social phobia, and binge eating disorder. SynthAgent integrates clinical and medical evidence from claims data, population surveys, and patient-centered literature to construct personalized virtual patients enriched with personality traits that influence adherence, emotion regulation, and lifestyle behaviors. Through autonomous agent interactions, the system simulates disease progression, treatment response, and life management across diverse psychosocial contexts. Evaluation of more than 100 generated patients demonstrated that GPT-5 and Claude 4.5 Sonnet achieved the highest fidelity as the core engine in the proposed MAS framework, outperforming Gemini 2.5 Pro and DeepSeek-R1. SynthAgent thus provides a scalable and privacy-preserving framework for exploring patient journeys, behavioral dynamics, and decision-making processes in both medical and psychological domains.</p></div>
			</abstract>
```
#### Coherencia nº figures
Por pantalla se muestra nfigures: 6 (al igual que en `/generated_files/figures_visualization.png` sale que el paper1 tiene 6 figuras)
En el mismo `/xmls/paper1.tei.xml` en las líneas 108, 109, 110, 111, 112 y 113 encontramos las 6 figuras correspondientes, sin encontrar más en el paper
Además, si abrimos el pdf dicho, encontraremos las figuras en estas páginas, ni más ni menos:
1 - Figure 1: página 4
2 - Table 1: página 5
3 - Figure 2: página 6
4 - Table 2: página 6
5 - Table 3: página 6
6 - Figure 3: página 7

#### Coherencia links
A la izquierda están puestos los links listados por pantalla, mientras que a la derecha la línea del paper1 en la que se encuentra el link:

```
1. https://github.com/kermitt2/grobid   |   línea 61
2. https://wwwn.cdc.gov/nchs/nhanes/.Hyattsville    |   línea 307
3. https://www.cdc.gov/brfss/index.htm  |   línea 320
4. https://data.worldobesity.org/country/united-states-227/.GlobalObesityObservatory    |  línea 806
5. https://openai.com/gpt-5/.Largelanguagemodel |   línea 866
6. https://www.anthropic.com/news/claude-sonnet-4-5.Largelanguagemodel  |   línea 920
7. https://purplelab.com    |   línea 90
```

El primero es un link de referencia que se genera al procesar los `.pdf` con GROBID, y el resto sí son del `.pdf`. Se ha observado que algunos enlaces extraídos por GROBID contienen fragmentos adicionales que no forman parte real de la URL. Esto se debe a que el PDF no almacena el texto de forma semántica, sino como fragmentos posicionados, y durante el proceso de reconstrucción del contenido GROBID puede concatenar texto adyacente al enlace, aunque el programa consiga sacar todos los links que encuentre GROBID.

#### Limpieza del abstract
Como podemos observar en la comparación del abstract y del abstract limpio, podemos ver que tanto signos de puntuación han desaparecido, se ha pasado el texto entero a minúsculas, hay palabras que han sido pasadas a su lexema, como por ejemplo offers -> offer (4ª palabra del abstract original y 5ª palabra del abstract limpio) y se han eliminado stopwords como 'a' (5ª palabra del abstract original)


## Limitaciones

- El programa depende de que GROBID esté correctamente ejecutándose
- Algunos enlaces puede que GROBID no los procese bien del pdf al .tei.xml
- El preprocesamiento elimina números, lo que puede suponer pérdida de información en ciertos contextos, en este caso se está usando únicamente para el conteo de palabras de los ficheros.




