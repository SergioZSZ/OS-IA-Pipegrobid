## Validaciones

Para realizar las siguientes validaciones se usó el documento `.pdf` encontrado en https://arxiv.org/pdf/2602.16435


### 1. Funcionamiento de GROBID

Se añadió un módulo en `src/pipegrobid/flow/auxiliar/isactive.py` codificando una función que realiza una peticion GET a la API de GROBID para verificar su funcionamiento con un timeout de 5 segundos. Se incorporó en el flujo del `src/pipegrobid/__main__.py` y puede ocurrir:
    - Devuelve un booleano `True` y se ejecuta el resto del código
    - Devuelve un booleano `False` y salta un aviso de que no se pudo conectar a GROBID

### 2. Coherencia con la extracción de abstracts, nº figures y links
Para verificar la Coherencia de los datos extraídos, se añadieron en el Script `/src/pipegrobid/flow/xml_processing.py` en la funcion `process_xml()` dos bloques de código:

- 1º (líneas 66-77): Para el primer paper generado (correspondiente al pdf mencionado al principio de este bloque) se imprime por pantalla el nombre del paper, el abstract extraído, su número de figuras y links (posteriormente añadidas al diccionario que se envía al `__main__.py`), Saliendo por pantalla:
```
***************************** VALIDACION ***************************** 

paper: xmls\paper1.tei.xml

abstract:
 Simulating high-fidelity patients offers a powerful avenue for studying complex diseases while addressing the challenges of fragmented, biased, and privacy-restricted real-world data. In this study, we introduce SynthAgent, a novel Multi-Agent System (MAS) framework designed to model obesity patients with comorbid mental disorders, including depression, anxiety, social phobia, and binge eating disorder. SynthAgent integrates clinical and medical evidence from claims data, population surveys, and patient-centered literature to construct personalized virtual patients enriched with personality traits that influence adherence, emotion regulation, and lifestyle behaviors. Through autonomous agent interactions, the system simulates disease progression, treatment response, and life management across diverse psychosocial contexts. Evaluation of more than 100 generated patients demonstrated that GPT-5 and Claude 4.5 Sonnet achieved the highest fidelity as the core engine in the proposed MAS framework, outperforming Gemini 2.5 Pro and DeepSeek-R1. SynthAgent thus provides a scalable and privacy-preserving framework for exploring patient journeys, behavioral dynamics, and decision-making processes in both medical and psychological domains.

nfigures: 6

links: ['https://github.com/kermitt2/grobid', 'https://wwwn.cdc.gov/nchs/nhanes/.Hyattsville', 'https://www.cdc.gov/brfss/index.htm', 'https://data.worldobesity.org/country/united-states-227/.GlobalObesityObservatory', 'https://openai.com/gpt-5/.Largelanguagemodel', 'https://www.anthropic.com/news/claude-sonnet-4-5.Largelanguagemodel', 'https://purplelab.com']
```

- 2º (líneas 118-128): se muestra por pantalla el abstract limpio y lematizado para ver qué palabras se repiten más, por pantalla muestra esa parte del código:
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
1. https://wwwn.cdc.gov/nchs/nhanes/.Hyattsville    |   línea 307
2. https://www.cdc.gov/brfss/index.htm  |   línea 320
3. https://data.worldobesity.org/country/united-states-227/.GlobalObesityObservatory    |  línea 806
4. https://openai.com/gpt-5/.Largelanguagemodel |   línea 866
5. https://www.anthropic.com/news/claude-sonnet-4-5.Largelanguagemodel  |   línea 920
6. https://purplelab.com    |   línea 90
```

Se ha observado que algunos enlaces extraídos por GROBID contienen fragmentos adicionales que no forman parte real de la URL. Esto se debe a que el PDF no almacena el texto de forma semántica, sino como fragmentos posicionados, y durante el proceso de reconstrucción del contenido GROBID puede concatenar texto adyacente al enlace, aunque el programa consiga sacar todos los links que encuentre GROBID.

#### Limpieza del abstract
Como podemos observar en la comparación del abstract y del abstract limpio, podemos ver que tanto signos de puntuación han desaparecido, se ha pasado el texto entero a minúsculas, hay palabras que han sido pasadas a su lexema, como por ejemplo offers -> offer (4ª palabra del abstract original y 5ª palabra del abstract limpio) y se han eliminado stopwords como 'a' (5ª palabra del abstract original)
