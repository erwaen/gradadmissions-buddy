from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import weaviate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from jsonSplitter import *
import weaviateHandler
import uvicorn
import weaviateQuery

load_dotenv()
app = FastAPI()
client = weaviate.Client('http://weaviate:8080/')



# Initialize OpenAI model
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

@app.get("/query/")
async def query_response(prompt):
    return weaviateQuery(prompt)
# Endpoint to retrieve scrapped data from the crawler module
@app.get("/get-data/")
async  def get_data():

    raise NotImplementedError

# Endpoint to process and split data
@app.post("/split-data/")
async def process_data():
    splitter = DataSplitter('data.json', 'out.json')
    splitter.process_data()

# Endpoint to insert processed data into Weaviate
@app.post("/insert-data/")
async def insert_data():
    weaviate_url = "http://weaviate:8080" 
    json_file = 'out.json'
    weaviateHandler.insert_into_weaviate(json_file, weaviate_url)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=False)
