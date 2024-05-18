from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import weaviate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
import uuid
import weaviateHandler
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Weaviate client
client = weaviate.Client('http://weaviate:8080/')

# Initialize OpenAI model
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

class DataSplitter:
    """Class to handle splitting of large text data into smaller chunks."""

    def __init__(self, input_file, output_file, chunk_size=100):
        """
        Initialize the DataSplitter with input/output file paths and chunk size.
        
        Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to the output JSON file.
        chunk_size (int): Maximum number of characters per chunk.
        """
        self.input_file = input_file
        self.output_file = output_file
        self.chunk_size = chunk_size

    def load_data(self):
        """Load data from a JSON file."""
        with open(self.input_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_data(self, data):
        """Save processed data to a JSON file."""
        with open(self.output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def split_content(self, content):
        """
        Split content into chunks based on the specified size.
        
        Args:
        content (str): The content string to be split into chunks.
        
        Returns:
        list: A list of content chunks.
        """
        words = content.split()
        chunks = []
        current_chunk = []
        current_length = 0

        # Iterate over words and split into chunks
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
        """Process data to create chunks with linkage and save to output file."""
        data = self.load_data()
        processed_data = []

        for entry in data:
            content_chunks = self.split_content(entry['content'])
            chunk_uuids = [str(uuid.uuid4()) for _ in range(len(content_chunks))]
            previous_id = None

            for i, chunk in enumerate(content_chunks):
                chunk_id = chunk_uuids[i]
                next_id = chunk_uuids[i + 1] if i < len(content_chunks) - 1 else None

                chunk_entry = {
                    "id": str(uuid.uuid4()),
                    "url": entry['url'],
                    "university_name": entry['university_name'],
                    "content": chunk,
                    "chunk_id": chunk_id,
                    "previous_id": previous_id,
                    "next_id": next_id
                }
                processed_data.append(chunk_entry)
                previous_id = chunk_id

        self.save_data(processed_data)

# Endpoint to process and split data
@app.post("/update-DB/")
async def process_data():
    splitter = DataSplitter('data.json', 'out.json')
    splitter.process_data()

# Endpoint to insert processed data into Weaviate
@app.post("/insert-Data/")
async def insert_data():
    weaviate_url = "http://weaviate:8080"  # Replace with your Weaviate instance URL
    json_file = 'out.json'
    weaviateHandler.insert_into_weaviate(json_file, weaviate_url)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=False)
