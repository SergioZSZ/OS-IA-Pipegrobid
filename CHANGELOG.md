
# Novedades

## Parseo de XMLs generados por grobid

- añadidos scripts para la extracción de información estructurada:

    - initial_parse.py:
        contiene funciones para el parseo de los datos estructurados del xml generado a partir
        del pdf con los que se puede nutrir el KG

    - parse_grobid_xml.py:
        contiene el flujo de parseo del xml para obtener los datos estructurados y creación
        de jsons estructurados con dichos datos

## Próximas integraciones
- Generación de TopicModeling mediante Transformers (BERTopic) usado para nutrir el KG con los Topics generados y con qué papers está relacionado.

- Uso de LLM para reconocimiento de entidades en "acknowledgements" para nutrir el KG con las relaciones de acknowledges y sus rangos(Person,Organization) y posiblemente Projects

- Creación del KG a partir de los datos obtenidos tanto de manera estructurada como gracias a IA.

- Nutrir KG creado con información obtenida de otros KGs (OpenAire, ORCID, Wikidata) 

