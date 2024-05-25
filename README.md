# gradadmissions-buddy

## Descripción del Proyecto

**gradadmissions-buddy** es un proyecto desarrollado para la materia "Ingeniería de Software 2" por Julia Recalde y Carlos Troya. El objetivo del proyecto es crear una aplicación que gestione y procese datos de admisiones universitarias utilizando FastAPI, Weaviate y OpenAI. La aplicación actúa como un sistema de Recuperación de Información con Generación Automática (RAG), que scrapea páginas web de universidades para luego dar contexto a un modelo de lenguaje (LLM) que se encarga de responder las preguntas.

## Sección 1: Levantando el Proyecto con Docker

El proyecto se despliega utilizando Docker y Docker Compose. Para iniciar la aplicación, asegúrate de tener Docker y Docker Compose instalados en tu máquina.

### Servicios Incluidos

- **backend_db**: Este servicio ejecuta la aplicación FastAPI que gestiona los endpoints para procesar y almacenar datos.
- **weaviate**: Una base de datos vectorial utilizada para almacenar y consultar datos procesados.
- **contextionary**: Proporciona servicios de vectorización para Weaviate.
- **Univspider**: Proporciona servicios de web-scraping mediante FastAPI.

### Comandos para Levantar el Proyecto

Para levantar el proyecto, navega al directorio raíz del repositorio y ejecuta:

```bash
docker-compose up --build
```

Este comando construirá las imágenes Docker necesarias y levantará todos los servicios definidos en el archivo `docker-compose.yaml`.

```yaml
services:
  backend_db:
    # Configuración del servicio de Backend_DB
  weaviate:
    # Configuración del servicio Weaviate
  contextionary:
    # Configuración del servicio Contextionary
  univspider:
    # Configuración del servicio univspider
networks:
  app-network:
    driver: bridge
```

## Sección 2: Endpoints de la API

### `/buffer/insert-data/` (POST)

Inserta datos en el buffer para su posterior procesamiento.

| Método | Endpoint              | Descripción                           | Ejemplo de Input         | Ejemplo de Output                   |
|--------|-----------------------|---------------------------------------|--------------------------|-------------------------------------|
| POST   | /buffer/insert-data/  | Inserta datos en el buffer            | `[{"url": "http://..."}]`| `{"message": "Buffer updated successfully"}`|

Ejemplo de uso:
```bash
curl -X POST http://localhost:69/buffer/insert-data/ -d '[{"url": "http://example.com"}]'
```

### `/split-Data/` (POST)

Procesa y divide en chunks a los datos que esten en el buffer.

| Método | Endpoint      | Descripción                           | Ejemplo de Input | Ejemplo de Output         |
|--------|---------------|---------------------------------------|------------------|---------------------------|
| POST   | /split-Data/  | Procesa y divide los datos en chunks  | N/A              | `{"message": "Data processed and split successfully"}"}`|

Ejemplo de uso:
```bash
curl -X POST http://localhost:69/split-Data/
```

### `/insert-Data/` (POST)

Inserta datos procesados en Weaviate.

| Método | Endpoint      | Descripción                            | Ejemplo de Input | Ejemplo de Output            |
|--------|---------------|----------------------------------------|------------------|------------------------------|
| POST   | /insert-Data/ | Inserta datos procesados en Weaviate   | N/A              | `{"message": "Data inserted into Weaviate successfully"}`|

Ejemplo de uso:
```bash
curl -X POST http://localhost:69/insert-Data/
```

### `/query/` (GET)

Consulta la base de datos vectorial en Weaviate para obtener información basada en un prompt.

| Método | Endpoint  | Descripción                                                | Ejemplo de Input                        | Ejemplo de Output                                                                                                         |
|--------|-----------|------------------------------------------------------------|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| GET    | /query/   | Realiza una consulta en Weaviate utilizando un prompt dado | `/query/?prompt=Harvard&n_items=1`      | `{"data": {"Get": {"UniversityData": [{"chunk_id": "123", "content": "example content", "url": "http://example.com"}]}}}` |

Ejemplo de uso:
```bash
curl -X GET "http://localhost:69/query/?prompt=Harvard&n_items=1"
```



## Sección 3: Funcionamiento del Proyecto

### Diagrama de Flujo

A continuación se muestra un diagrama de flujo creado con Excalidraw que ilustra los pasos del procesamiento de datos desde la entrada de un string hasta la respuesta de la API:

![Diagrama de Flujo](https://drive.google.com/uc?id=1lEG2lBW4hSVra9y34AY7iyB7BXb0Xn3_)

### Estructura de los Datos en la DB Vectorizada

Los datos se almacenan en Weaviate en una estructura vectorial. Cada entrada contiene los siguientes metadatos:

- **url**: URL de la fuente de datos.
- **university_name**: Nombre de la universidad.
- **content**: Texto del contenido dividido en chunks.
- **chunk_id**: ID único del chunk.
- **previous_id**: ID del chunk anterior.
- **next_id**: ID del siguiente chunk.

Cada chunk contiene un máximo de 100 caracteres.

### Consulta al Crawler y Almacenamiento en la DB

El proceso para conseguir los datos y almacenarlos en la DB vectorizada incluye los siguientes pasos:

1. **Consulta al Crawler**: El endpoint `/get-data/` se diseña para solicitar datos al crawler y almacenarlos en `data.json`.
2. **Procesamiento de Datos**: El endpoint `/split-Data/` utiliza la clase `DataSplitter` para dividir los datos en chunks manejables.
3. **Inserción en Weaviate**: El endpoint `/insert-Data/` inserta los datos procesados en Weaviate.

## Ejemplo de Uso

```bash
# Insertar datos en el buffer
curl -X POST http://localhost:69/buffer/insert-data/ -d '[{"url": "http://example.com"}]'

# Procesar y dividir datos
curl -X POST http://localhost:69/split-Data/

# Insertar datos procesados en Weaviate
curl -X POST http://localhost:69/insert-Data/

# Consultar datos en Weaviate
curl -X GET "http://localhost:69/query/?prompt=Harvard&n_items=1"
```

Este `README.md` proporciona una visión general completa del proyecto, incluyendo cómo levantarlo con Docker, los detalles de los endpoints de la API y el flujo de funcionamiento del sistema.
