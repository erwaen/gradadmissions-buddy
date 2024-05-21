from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import weaviate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from jsonSplitter import DataSplitter
import weaviateHandler
import uvicorn
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Weaviate client
client = weaviate.Client(os.getenv('WEAVIATE_URL', 'http://weaviate:8080'))

# Initialize OpenAI model
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

@app.get("/query/")
async def query_response(prompt: str):
    return weaviateHandler.query_weaviate(prompt)

# Endpoint to retrieve scrapped data from the crawler module
@app.get("/get-data/")
async def get_data():
    #voy a harcodear el endpoint de julia, y añadir al data.json los objetos del response del request
    raise NotImplementedError

# Endpoint to process and split data
@app.post("/split-data/")
async def process_data():
    splitter = DataSplitter('archivos_json/university_1.json', 'out.json')
    splitter.process_data()
    return {"message": "Data processed and split successfully"}

# Endpoint to insert processed data into Weaviate
@app.post("/insert-data/")
async def insert_data():
    weaviate_url = "http://weaviate:8080"
    json_file = 'out.json'
    weaviateHandler.insert_into_weaviate(json_file, weaviate_url)
    return {"message": "Data inserted into Weaviate successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=False)
