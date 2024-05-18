# Crawler Microservice

## Descripción

Este proyecto es un microservicio desarrollado con FastAPI para facilitar el acceso a documentos scrapeados de universidades. Proporciona varios endpoints para interactuar con los datos scrapeados.

## Tabla de Contenidos

- [Instalación](#instalación)
- [Uso](#uso)
- [Endpoints](#endpoints)

## Instalación

1. Clona el repositorio:

    ```bash
    git clone https://github.com/erwaen/gradadmissions-buddy.git
    cd gradadmissions-buddy
    ```

2. Instala las dependencias:

    ```bash
    pip3 install -r requirements.txt
    ```
## Uso

### Correr el Crawler

Para iniciar el proceso de scraping y obtener los documentos de las universidades, ejecuta el siguiente comando:

```bash
scrapy crawl university
```
Para correr el crawler y obtener documentos de algunas universidades específicas, utiliza el comando -a seguido del parámetro correspondiente. Por ejemplo, para especificar una lista de universidades con el id 1, 3, 5

##### Lista de universidades:
| ID | NOMBRE                     |
|----|----------------------------|
| 1  | University of Chicago      |
| 2  | Princeton University       |
| 3  | Cornell University         |
| 4  | Columbia University        |
| 5  | Johns Hopkins University   |
| 6  | University of Michigan     |
| 7  | University of Rochester    |
| 8  | Harvard University         |
| 9  | Stanford University        |
| 10 | University of Oxford       |

```bash
scrapy crawl university -a universities=<ID>
```
### Estructura del archivo JSON

Cada archivo JSON contiene un array de objetos donde cada objeto representa un elemento scrapeado del sitio web de la universidad. La estructura de cada objeto es la siguiente:

```json
[
    {
        "id": "El ID único del elemento scrapeado",
        "date": "La fecha y hora en que se realizó el scrapeo",
        "url": "La URL del sitio web de la universidad de donde se extrajeron los datos",
        "university_name": "El nombre de la universidad correspondiente",
        "title": "El título del contenido scrapeado, si está disponible",
        "content": "El contenido scrapeado, que puede incluir texto"
    },
    ...
]
```
### Ejemplo
Ejemplo de cómo podría verse un archivo JSON para la Universidad de Chicago:

```json
[
    {
        "id": 1,
        "date": "2024-05-17T19:20:35.819807",
        "url": "https://accessibility.uchicago.edu",
        "university_name": "University of Chicago",
        "title": "Access UChicago Now",
        "content": "The University of Chicago Home About Leadership Team 2023-2024 Academic Year 2022-2023 Academic Year 2021-2022..." 
    },
    ...
]
```
## Iniciar el Microservicio

### Prerrequisitos

- Python 3.7 o superior
- FastAPI
- Uvicorn

### Instalación de Dependencias

Asegúrate de que todas las dependencias estén instaladas. Si aún no lo has hecho, ejecuta:

```bash
pip3 install -r requirements.txt
```

### Para iniciar el microservicio, utiliza el siguiente comando:

```bash
uvicorn main:app --reload
```





