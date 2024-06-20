from fastapi import Depends, FastAPI, HTTPException
from typing import Generator, List
import weaviate
from dotenv import load_dotenv
import weaviateHandler
import jsonSplitter
import json
from models import UniversityData
import requests

WEAVIATE_URL = 'http://weaviate:8080'

# Load environment variables
load_dotenv()

app = FastAPI()

async def get_weaviate_client():
    wclient = weaviate.connect_to_local(host="weaviate")
    try:
        yield wclient
    finally:
        wclient.close()
# Initialize Weaviate client

@app.get("/query/")
async def query_response(
        prompt: str,
        n_items: int = 5,
        wclient: weaviate.client.WeaviateClient = Depends(get_weaviate_client)
    ):

    return weaviateHandler.query_weaviate(wclient, prompt, n_items)

# Endpoint to retrieve scrapped data from the crawler module
@app.get("/get-data/")
async def get_data():
    raise HTTPException(status_code=501, detail="This feature is not implemented yet")


# Endpoint to process and split data
@app.post("/split-data/")
async def process_data():
    splitter = jsonSplitter.DataSplitter('data.json', 'out.json')
    splitter.process_data()
    return {"message": "Data processed and split successfully"}

# Endpoint to insert processed data into Weaviate
@app.post("/insert-data/")
async def insert_data(wclient = Depends(get_weaviate_client)):
    json_file = 'out.json'
    ret = weaviateHandler.insert_into_weaviate(wclient,json_file)
    if ret != {"message": "Data inserted into Weaviate successfully"}:
        raise HTTPException(status_code=500, detail=ret)
    open(json_file, 'w').close()  # Limpiamos out.json
    open('data.json', 'w').close()  # Limpiamos data.json
    dataJson = open('data.json', 'w')
    dataJson.write('[]')
    return ret

@app.post("/buffer/insert-data/")
async def buffer_insert_data(new_data: List[UniversityData], wclient = Depends(get_weaviate_client)):
    payloadDict = [dict(item) for item in new_data]
    try:
        with open("data.json", "r", encoding="utf-8") as json_file:
            bufferInFile = json.load(json_file)
            bufferInFileDict = [dict(item) for item in bufferInFile]
    except:
        dataJson = open('data.json', 'w')
        dataJson.write('[]')
        dataJson.close()
        with open("data.json", "r", encoding="utf-8") as json_file:
            bufferInFile = json.load(json_file)
            bufferInFileDict = [dict(item) for item in bufferInFile]
    for item in payloadDict:
        bufferInFileDict.append(item)
    newBufferWithoutDuplicates = []
    for elem in bufferInFileDict:
        if elem not in newBufferWithoutDuplicates:
            newBufferWithoutDuplicates.append(elem)
    with open("data.json", "w", encoding="utf-8") as json_file:
        json.dump(newBufferWithoutDuplicates, json_file)
    return {"message": "Buffer updated successfully"}

@app.post("/retrieve/crawler")
async def retrieve_data(wclient = Depends(get_weaviate_client)):
    for i in range(1, 9):
        response = requests.post("http://univspider:81/universidades/", json={"id": i, "desde": 0, "hasta": 10})
        if response.status_code == 200:
            data = response.json()
            await buffer_insert_data(data)  # Directly call the buffer insert function
        else:
            return {"message": f"Failed to retrieve data for university id {i}", "status_code": response.status_code}
    
    # Split data after all data has been inserted into the buffer
    await process_data()  # Directly call the split data function
    # Insert data into Weaviate after splitting
    await insert_data(wclient)  # Directly call the insert data function

    return {"message": "Data retrieved, processed, and inserted successfully"}
@app.head("/health")
async def xd():
    return True
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=80, reload=False)
