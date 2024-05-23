from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import weaviate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import weaviateHandler
import uvicorn
import os
# import orjson
import json
from models import UniversityData
import jsonSplitter
import requests
# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Weaviate client
client = weaviate.Client(os.getenv('WEAVIATE_URL', 'http://weaviate:8080'))

# Initialize OpenAI model
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

@app.get("/query/")
async def query_response(prompt: str, n_items : int = 5):
    return weaviateHandler.query_weaviate(prompt,n_items)

# Endpoint to retrieve scrapped data from the crawler module
@app.get("/get-data/")
async def get_data():
    raise NotImplementedError

# Endpoint to process and split data
@app.post("/split-data/")
async def process_data():
    splitter = jsonSplitter.DataSplitter('data.json', 'out.json')
    splitter.process_data()
    return {"message": "Data processed and split successfully"}

# Endpoint to insert processed data into Weaviate
@app.post("/insert-data/")
async def insert_data():
    weaviate_url = "http://weaviate:8080"
    json_file = 'out.json'
    weaviateHandler.insert_into_weaviate(json_file, weaviate_url)
    open(json_file, 'w').close() #Limpiamos out.json
    open('data.json', 'w').close() #Limpiamos data.json
    dataJson = open('data.json','w')
    dataJson.write('[]')
    return {"message": "Data inserted into Weaviate successfully"}



@app.post("/buffer/insert-data/")
async def buffer_insert_data(new_data: List[UniversityData]):
    # print(new_data)
    payloadDict = [dict(item) for item in new_data]
    # res = json.dumps(toDict)
    try:
        with open("data.json","r",encoding="utf-8") as json_file:
            bufferInFile = json.load(json_file)
            bufferInFileDict = [dict (item) for item in bufferInFile]
    except:
        dataJson = open('data.json','w')
        dataJson.write('[]')
        dataJson.close()
        with open("data.json","r",encoding="utf-8") as json_file:
            bufferInFile = json.load(json_file)
            bufferInFileDict = [dict (item) for item in bufferInFile]
    for item in payloadDict:
        bufferInFileDict.append(item) 
    newBufferWithoutDuplicates = []
    for elem in bufferInFileDict:
        if elem not in newBufferWithoutDuplicates:
            newBufferWithoutDuplicates.append(elem)
    with open("data.json","w",encoding="utf-8") as json_file:
        json.dump(newBufferWithoutDuplicates,json_file)
    return {"message":"Buffer updated successfully"}
@app.post("/retrieve-data/")
async def retrieve_data():
    for i in range(1,9):
        requests.post("localhost:8080")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=False)
