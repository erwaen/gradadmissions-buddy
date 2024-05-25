import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import glob
from fastapi.responses import FileResponse
import zipfile
import requests

class GetDocumentosIN (BaseModel):
    id: int
    
class QueryRequest(BaseModel):
    id: int
    title: str
    
class DataInsertionError(Exception):
    """Raised when there is an error inserting data into the microservice."""
    pass

app = FastAPI()

# Archivo temporal para almacenar el buffer
buffer_file = "data.json"
archivo_chunk= "archivos_chunk"
data_file = 'data.json'
output_file = 'out.json'
chunk_size = 10

class Universidad(BaseModel):
    id: int
    date: str
    url: str
    university_name: str
    title: str
    content: str

def read_json_file(university_id):
    filename = f'archivos_json/university_{university_id}.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_university_name(university_id: int) -> str:
    folder_path = f"dataset/university{university_id}"
    json_files = glob.glob(os.path.join(folder_path, "documento*.json"))
    if not json_files:
        return "Unknown"
    with open(json_files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("university_name", "Unknown")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/universidades/")
async def get_documentos(body: GetDocumentosIN):
    documentos = read_json_file(body.id)
    if not documentos:
        raise HTTPException(status_code=404, detail="Document not found")

    return documentos

@app.post("/universidades/consulta-titulo/")
async def query_title(title: str):
    try:
        files = glob.glob("archivos_json/university_*.json")
        results = []
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            for item in data:
                if "title" in item and title.lower() in item["title"].lower():
                    results.append(item)   
        if not results:
            raise HTTPException(status_code=404, detail="Title not found in any document")
        return results
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No documents found")
    
@app.get("/universidades/list", response_model=List[Dict[str, str]])
async def list_universidades():
    universidades = []
    for folder_name in os.listdir("dataset"):
        if folder_name.startswith("university"):
            university_id = folder_name[len("university"):]
            university_name = get_university_name(university_id)
            universidades.append({"id": university_id, "name": university_name})
    if not universidades:
        raise HTTPException(status_code=404, detail="No universities found")
    return universidades

@app.post("/enviar-datos/")
async def enviar_datos():
    try:
        data = []
        # Leer los datos scrapeados de los 10 archivos JSON correspondientes a las universidades
        for i in range(1, 11):
            filename = f"archivos_json/university_{i}.json"
            with open(filename, "r", encoding="utf-8") as f:
                data.extend(json.load(f))
                
        # Guardar los datos en el archivo buffer
        with open(buffer_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # Enviar los datos scrapeados al microservicio
        url_microservicio = "http://localhost:69/buffer/insert-data/"
        response = requests.post(url_microservicio, json=data)

        if response.status_code == 200:
            return {"message": "Datos scrapeados enviados correctamente al microservicio"}
        else:
            raise HTTPException(status_code=response.status_code, detail="Error al enviar los datos al microservicio")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=81)