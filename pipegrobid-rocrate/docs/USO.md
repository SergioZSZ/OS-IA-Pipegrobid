## Ejecución del software
Tras seguir los pasos de instalación y preparación del entorno, se deben meter los pdfs a procesar en el directorio `/pdfs`. Tras ello, ejecutar en el directorio raíz el mandato `poetry run pipegrobid`. Tras ello, se generarán los ficheros `.tei.xml` en el directorio `/xmls` y los ficheros con el keyword cloud, nº figuras y links de los pdfs en el directorio `generated_files`

## Ejecución de los test
Para ejecutar los test, se debe realizar en la carpeta raíz del proyecto el mandato `poetry run pytest -v`