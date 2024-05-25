# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt de tests al contenedor
COPY tests/requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de tests al contenedor
COPY . .

# Copia el contenido del backend al contenedor
COPY ../backend /app/backend

ENV PYTHONPATH=/app/backend

# Comando para ejecutar los tests
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-v"]
