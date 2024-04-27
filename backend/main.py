from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import weaviate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()


client = weaviate.Client('http://weaviate:8080/')


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

class QueryInput(BaseModel):
    query: str

class QueryOutput(BaseModel):
    response: str

import json

class DataSplitter:
    def __init__(self, input_file, output_file, chunk_size=500):
        self.input_file = input_file
        self.output_file = output_file
        self.chunk_size = chunk_size  # Max characters per chunk

    def load_data(self):
        with open(self.input_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_data(self, data):
        with open(self.output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def split_content(self, content):
        words = content.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > self.chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def process_data(self):
        data = self.load_data()
        processed_data = []
        last_id = None

        for item in data:
            chunks = self.split_content(item['content'])
            for i, chunk in enumerate(chunks):
                new_item = {
                    'id': f"{item['id']}_{i}",
                    'url': item['url'],
                    'university_name': item['university_name'],
                    'content': chunk,
                    'next_id': f"{item['id']}_{i+1}" if i < len(chunks) - 1 else None
                }
                processed_data.append(new_item)

        self.save_data(processed_data)

@app.post("/update-DB/")
async def process_data():
    splitter = DataSplitter('data.json', 'out.json')
    splitter.process_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80,reload=False)
