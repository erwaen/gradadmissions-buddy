from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import weaviate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
import json
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
        """Load data from a JSON file."""
        with open(self.input_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_data(self, data):
        """Save processed data to a JSON file."""
        with open(self.output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def split_content(self, content):
        """Split content into chunks based on specified size."""
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
        """Process data to create chunks with linkage."""
        data = self.load_data()
        processed_data = []

        for entry in data:
            content_chunks = self.split_content(entry['content'])
            previous_id = None

            for i, chunk in enumerate(content_chunks):
                chunk_id = i
                next_id = i+1 if i < len(content_chunks) - 1 else None

                chunk_entry = {
                    "id": entry['id'],
                    "url": entry['url'],
                    "university_name": entry['university_name'],
                    "content": chunk,
                    "chunk_id": i,
                    "previous_id": previous_id,
                    "next_id": next_id
                }
                processed_data.append(chunk_entry)
                previous_id = chunk_id 
        self.save_data(processed_data)





class UniversityDataHandler:
    def __init__(self, weaviate_url):
        self.client = weaviate.Client(weaviate_url)
        self.setup_schema()

    def setup_schema(self):
        schema = {
            "classes": [
                {
                    "class": "University",
                    "properties": [
                        {"name": "url", "dataType": ["string"], "indexInverted": True},
                        {"name": "university_name", "dataType": ["string"], "indexInverted": True},
                    ]
                },
                {
                    "class": "UniversityPage",
                    "properties": [
                        {"name": "content", "dataType": ["text"], "indexInverted": True},
                        {"name": "university", "dataType": ["University"], "cardinality": "atMostOne"},
                        {"name": "next_chunk", "dataType": ["UniversityPage"], "cardinality": "atMostOne"},
                    ]
                }
            ]
        }
        self.client.schema.delete_all()
        self.client.schema.create(schema)

    def add_university(self, uuid, url, name):

        university_object = {
            "url": url,
            "university_name": name
        }
        self.client.data_object.create(university_object, "University", uuid)

    def add_university_page(self, uuid, content, university_uuid, next_chunk_uuid=None):
        page_object = {
            "content": content,
            "university": {
                "beacon": f"weaviate://localhost/University/{university_uuid}"
            }
        }
        self.client.data_object.create(page_object, "UniversityPage", uuid)
        if next_chunk_uuid:
            self.client.data_object.add_reference(uuid, "UniversityPage", "next_chunk", next_chunk_uuid)


# handler = UniversityDataHandler('http://localhost:8080')
# handler.add_university("univ-harvard", "https://college.harvard.edu/admissions", "Harvard University")
# handler.add_university_page("page1", "Page content 1", "univ-harvard", "page2")
# handler.add_university_page("page2", "Page content 2", "univ-harvard")

@app.post("/update-DB/")
async def process_data():
    splitter = DataSplitter('data.json', 'out.json')
    splitter.process_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80,reload=False)
