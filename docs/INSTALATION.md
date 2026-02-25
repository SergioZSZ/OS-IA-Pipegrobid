## Requisitos previos

- Docker y Docker Desktop
- Python >= 3.10
- Software `GROBID`: https://github.com/kermitt2/grobid
- Gestor de dependencias `poetry`

- Dependencias de Python usadas:
    -   `requests`: realización de peticiones a APIs
    -   `wordcloud`:    creación del wordcloud
    -   `matplotlib`:   generación y visualización de imágenes (wordcloud y figuras)
    -   `natsort`:  ordenación natural de strings 
    -   `nltk`: procesamiento del lenguaje natural(stopwords, lemmatizer)
    -   `pytest`: opcional, usada para correr los test


## Instrucciones de preparación del entorno, instalación y ejecución:

### Forma 1: Ejecución mediante docker-compose
Teniendo abierto Docker Desktop, desde el terminal (en el directorio base del proyecto `/`), donde está ubicado el fichero `docker-compose.yml` podemos ejecutar el mandato `docker compose up -d` para levantar tanto el servicio de GROBID como el de PipeGrobid. Para que funcione, antes de realizar el mandato se deben meter en la carpeta pdfs los `.pdf` que se quieran procesar.

Tras la ejecución y generación de archivos en el directorio `/generated_files` se debe realizar el mandato `docker compose down` para terminar el servicio de GROBID (ya que PipeGrobid terminará tras la generación de archivos).

### Forma 2: Instalación manual con poetry
Antes de nada, es necesario tener GROBID ejecutado. Para ello debemos abrir Docker Desktop/Docker y ejecutar en el terminal `docker run -t --rm -p 8070:8070 grobid/grobid:0.7.2`(para terminar su ejecución, desde el mismo terminal que se ejecutó hacer `Cntrl+C`) Una vez ejecutado, el siguiente paso es configurar el entorno.

Este proyecto utiliza `poetry` para la gestión de dependencias y del entorno virtual, garantizando reproducibilidad y aislamiento del entorno de ejecución.
-   Instalar poetry con `pip install poetry`
-   Una vez instalado `poetry` es necesario seguir estos pasos para poder replicarlo:
    
    1. Desde la raíz del proyecto, donde se encuentra `pyproyect.toml` ejecutar el mandato `poetry install` para crear el entorno e instalar dependencias necesarias

    2. ejecutar uno de estos dos mandatos para ejecutarlo desde ese mismo directorio:
        - `poetry run python -m pipegrobid` (ejecuta el __main__ del paquete pipegrobid con el flujo del proyecto)
        - `poetry run pipegrobid` (usa el entry point declarado en el``pyproject.toml``)