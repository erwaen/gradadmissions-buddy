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



class DataSplitter:
    def __init__(self, input_file, output_file, chunk_size=500):
        self.input_file = input_file
        self.output_file = output_file
        self.chunk_size = chunk_size

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
        """Add a university object to Weaviate."""
        university_object = {
            "url": url,
            "university_name": name
        }
        self.client.data_object.create(university_object, "University", uuid)

    def add_university_page(self, uuid, content, university_uuid, next_chunk_uuid=None):
        """Add a university page object to Weaviate with optional reference to the next chunk."""
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
