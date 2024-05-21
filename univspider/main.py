import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import glob
from fastapi.responses import FileResponse
import zipfile

class GetDocumentosIN (BaseModel):
    id: int
    desde: int
    hasta: int
    
class QueryRequest(BaseModel):
    id: int
    title: str
    
app = FastAPI()

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

    if body.desde is not None and body.hasta is not None:
        documentos = documentos[body.desde:body.hasta]
    return documentos

@app.post("/universidades/consulta/")
async def query_university(request: QueryRequest):
    id = request.id
    title = request.title
    try:
        with open(f"archivos_json/university_{id}.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        for item in data:
            if "title" in item and item["title"] == title:
                return item
        raise HTTPException(status_code=404, detail="Title not found")
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="University not found")

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

@app.get("/universidades/download/all")
async def download_dataset():
    zip_filename = "dataset_university.zip"
    zip_filepath = os.path.join("dataset", zip_filename)
    
    # Eliminar el archivo ZIP si ya existe
    if os.path.exists(zip_filepath):
        os.remove(zip_filepath)
    
    # Crear un nuevo archivo ZIP
    with zipfile.ZipFile(zip_filepath, "w") as zipf:
        for folder_name in os.listdir("dataset"):
            if folder_name.startswith("university"):
                folder_path = os.path.join("dataset", folder_name)
                json_files = glob.glob(os.path.join(folder_path, "documento*.json"))
                for json_file in json_files:
                    zipf.write(json_file, os.path.relpath(json_file, "dataset"))