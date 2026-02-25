# 1.3.1

- Eliminados test unitarios dependientes de GROBID

# 1.3.0

- Añadida dockerización del proyecto

- Modificado __main__ para cambiar URL dependiendo de si se ejecutó mediante docker-compose o en local

- Modificada función `isactive(url)` para esperar 30 segundos a que GROBID sea accesible

# 1.2.0

- cambiado entorno virtual de `Python venv` a `poetry` debido a su buena gestión de dependencias, su compatibilidad con otros sistemas operativos y facilidad para replicar y lanzar el proyecto (modificado README.md con lo necesario para su uso)

- añadido entry point con `poetry` para mejorar la facilidad de ejecución del paquete `pipegrobid` usando solo el mandato `poetry run pipegrobid`

- modulado mejor el código para generar pruebas unitarias

- añadido tipado a los inputs y  outputs de las funciones 

- añadidos test unitarios

- añadida github action para correr los test al subir el proyecto

- compatibilidad con python >= 3.10

- añadido Readthedocs documentation





