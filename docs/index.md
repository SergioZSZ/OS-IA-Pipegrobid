[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18647861.svg)](https://doi.org/10.5281/zenodo.18647861)
![GitHub License](https://img.shields.io/github/license/SergioZSZ/Artificial-Intelligence-And-Open-Science-In-Research-Software-Engineering)
[![GitHub release](https://img.shields.io/github/v/release/SergioZSZ/Artificial-Intelligence-And-Open-Science-In-Research-Software-Engineering?include_prereleases)](https://github.com/SergioZSZ/Artificial-Intelligence-And-Open-Science-In-Research-Software-Engineering/releases)
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


## Estructura del proyecto
```
/ 
├── generated_files/                # Archivos generados tras ejecutar
│   ├── figures_visualization.png   
│   ├── keyword_cloud.png
│   └── links_per_paper.txt
│
├── pdfs/                       # Input de PDFs (meterlos aquí)
├── xmls/                       # Archivos XML generados (por GROBID)
├── CITATION.cff                # Cómo citar el software 
├── codemeta.json               # Metadatos del proyecto
├── LICENSE                     # Licencia del Software
├── README.md                   # Documentación         
├── poetry.lock                 # Resolución de dependencias de poetry
├── pyproject.toml              # Metadatos, dependencias, declaraciones del entorno
│
└── src/
│   │
│   └──pipegrobid/                  # Paquete con el main inicial del proyecto a ejecutar
│       ├── __main__.py             # Ejecutable del paquete pipegrobid con el flujo definido
│       │
│       └── flow/                   # Subpaquete con modulos sobre flujo del programa
│           ├── __init__.py
│           ├── generations.py       # Generación de los ficheros pedidos
│           ├── grobid_interaction.py   # Interacción con GROBID
│           ├── xml_processing.py       # Procesamiento de los ficheros .tei.xml
│           │
│           └── auxiliar/               # Subpaquete con modulos auxiliares
│               │
│               ├── clean_text.py           # Procesamiento de texto 
│               ├── environment.py          # Generación del entorno
│               └── dw_stopwrods.py         # Gestión de Stopwords y Lemmatizer 
│  
│
│
└── test/       # Código de los test corridos con pytest

    
```