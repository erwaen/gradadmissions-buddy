from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import weaviate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from jsonSplitter import DataSplitter
import weaviateHandler
import uvicorn
import os
import json

# Load environment variables
load_dotenv()
os.system("pip install python-multipart")#XD
app = FastAPI()

# Initialize Weaviate client
client = weaviate.Client(os.getenv('WEAVIATE_URL', 'http://weaviate:8080'))

# Initialize OpenAI model
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

@app.get("/db/query/")
async def query_response(prompt: str):
    return weaviateHandler.query_weaviate(prompt)

# Endpoint to buffer insert data
@app.post("/buffer/insert-data/")
async def buffer_insert_data(file: UploadFile = File(...)):
    try:
        # Read the uploaded file content
        file_content = await file.read()
        new_data = json.loads(file_content.decode('utf-8'))
        
        # Initialize existing_data as an empty list if out.json does not exist
        existing_data = []

        # Try to load existing data from out.json
        try:
            with open('out.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            pass  # If the file does not exist, continue with existing_data as an empty list
        
        # Append new data to existing data
        if isinstance(new_data, list):
            existing_data.extend(new_data)
        else:
            raise HTTPException(status_code=400, detail="Uploaded file must contain a JSON array")
        
        # Save the updated data back to out.json
        with open('out.json', 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        
        return {"message": "Data appended successfully"}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# Endpoint to process and split data
@app.post("/buffer/split-data/")
async def process_data():
    splitter = DataSplitter('archivos_json/university_1.json', 'out.json')
    splitter.process_data()
    return {"message": "Data processed and split successfully"}

# Endpoint to insert processed data into Weaviate
@app.post("/db/insert-data/")
async def insert_data():
    weaviate_url = "http://weaviate:8080"
    json_file = 'out.json'
    weaviateHandler.insert_into_weaviate(json_file, weaviate_url)
    return {"message": "Data inserted into Weaviate successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=False)
