from fastapi import FastAPI
from pydantic import BaseModel

class GetDocumentosIN (BaseModel):
    id: int
    desde: int
    hasta: int
    
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/universidades/")
async def getdocumentos(body: GetDocumentosIN):
    return body