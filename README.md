# gradadmissions-buddy

## Descripción del Proyecto

**gradadmissions-buddy** es un proyecto desarrollado para la materia "Ingeniería de Software 2" por Julia Recalde y Carlos Troya. El objetivo del proyecto es crear una aplicación que gestione y procese datos de admisiones universitarias utilizando FastAPI, Weaviate y OpenAI. La aplicación actúa como un sistema de Recuperación de Información con Generación Automática (RAG), que scrapea páginas web de universidades para luego dar contexto a un modelo de lenguaje (LLM) que se encarga de responder las preguntas.

## Sección 1: Levantando el Proyecto con Docker

El proyecto se despliega utilizando Docker y Docker Compose. Para iniciar la aplicación, asegúrate de tener Docker y Docker Compose instalados en tu máquina.

### Servicios Incluidos

- **backend_db**: Este servicio ejecuta la aplicación FastAPI que gestiona los endpoints para procesar y almacenar datos.
- **weaviate**: Una base de datos vectorial utilizada para almacenar y consultar datos procesados.
- **contextionary**: Proporciona servicios de vectorización para Weaviate.

### Comandos para Levantar el Proyecto

Para levantar el proyecto, navega al directorio raíz del repositorio y ejecuta:

```bash
docker-compose up --build
```

Este comando construirá las imágenes Docker necesarias y levantará todos los servicios definidos en el archivo `docker-compose.yaml`.

```yaml
services:
  backend_db:
    build:
      context: ./backend
    image: backend_db_img
    volumes:
      - ./backend:/usr/src/app/
    env_file:
      - ./backend/.env
    command: python main.py
    ports:
      - "69:80"
    networks:
      - app-network
    depends_on:
      - weaviate
  weaviate:
    # Configuración del servicio Weaviate
  contextionary:
    # Configuración del servicio Contextionary
networks:
  app-network:
    driver: bridge
```

## Sección 2: Endpoints de la API

### `/get-data/` (GET)

Solicita datos del crawler y los guarda en `data.json`.

| Método | Endpoint    | Descripción                          | Ejemplo de Input  | Ejemplo de Output |
|--------|-------------|--------------------------------------|-------------------|-------------------|
| GET    | /get-data/  | Solicita datos del crawler           | N/A               | No implementado   |

Ejemplo de uso:
```bash
curl -X GET http://localhost:69/get-data/
```

### `/split-Data/` (POST)

Procesa y divide los datos en chunks utilizando la clase `DataSplitter`.

| Método | Endpoint      | Descripción                           | Ejemplo de Input            | Ejemplo de Output          |
|--------|---------------|---------------------------------------|-----------------------------|----------------------------|
| POST   | /split-Data/  | Procesa y divide los datos en chunks  | N/A                         | `{"message": "Data split"}`|

Ejemplo de uso:
```bash
curl -X POST http://localhost:69/split-Data/
```

### `/insert-Data/` (POST)

Inserta datos procesados en Weaviate.

| Método | Endpoint      | Descripción                            | Ejemplo de Input            | Ejemplo de Output          |
|--------|---------------|----------------------------------------|-----------------------------|----------------------------|
| POST   | /insert-Data/ | Inserta datos procesados en Weaviate   | N/A                         | `{"message": "Data inserted"}`|

Ejemplo de uso:
```bash
curl -X POST http://localhost:69/insert-Data/
```

## Sección 3: Funcionamiento del Proyecto

### Diagrama de Flujo

A continuación se muestra un diagrama de flujo creado con Excalidraw que ilustra los pasos del procesamiento de datos desde la entrada de un string hasta la respuesta de la API:

![Diagrama de Flujo](https://drive.usercontent.google.com/u/0/uc?id=1lEG2lBW4hSVra9y34AY7iyB7BXb0Xn3_&export=download)

### Estructura de los Datos en la DB Vectorizada

Los datos se almacenan en Weaviate en una estructura vectorial. Cada entrada contiene los siguientes metadatos:

- **url**: URL de la fuente de datos.
- **university_name**: Nombre de la universidad.
- **content**: Texto del contenido dividido en chunks.
- **chunk_id**: ID único del chunk.
- **previous_id**: ID del chunk anterior.
- **next_id**: ID del siguiente chunk.

Cada chunk contiene un máximo de 100 caracteres.

### Consulta al Crawler y Almacenamiento en la DB (Para mantenimiento de datos

El proceso para conseguir los datos y almacenarlos en la DB vectorizada incluye los siguientes pasos:

1. **Consulta al Crawler**: El endpoint `/get-data/` se diseñará para solicitar datos al crawler y almacenarlos en `data.json`.
2. **Procesamiento de Datos**: El endpoint `/split-Data/` utiliza la clase `DataSplitter` para dividir los datos en chunks manejables.
3. **Inserción en Weaviate**: El endpoint `/insert-Data/` inserta los datos procesados en Weaviate.
