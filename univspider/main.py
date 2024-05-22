import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import glob
import uvicorn
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=False)