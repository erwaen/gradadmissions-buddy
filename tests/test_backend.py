import os
import sys
import inspect
import weaviate
import pytest
from fastapi.testclient import TestClient
import json
import time

# Set up paths
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from main import app, UniversityData

client = TestClient(app)

def setup_module(module):
    # Initialize Weaviate schema before running tests
    client = weaviate.Client(os.getenv('WEAVIATE_URL', 'http://weaviate:8080'))
    schema = {
        "classes": [
            {
                "class": "UniversityData",
                "description": "A university data schema for tests",
                "properties": [
                    {"name": "test_id", "dataType": ["int"]},
                    {"name": "date", "dataType": ["string"]},
                    {"name": "url", "dataType": ["string"]},
                    {"name": "university_name", "dataType": ["string"]},
                    {"name": "title", "dataType": ["string"]},
                    {"name": "content", "dataType": ["string"]},
                ]
            }
        ]
    }

    existing_schema = client.schema.get()
    class_names = [cls["class"] for cls in existing_schema.get("classes", [])]

    if "UniversityData" not in class_names:
        client.schema.create(schema)

    # Add a delay to ensure Weaviate has time to process the schema
    time.sleep(5)

def test_buffer_insert_data():
    file_path = os.path.join(currentdir, "payloadTest.json")
    file = json.load(open(file_path, "r"))
    parentdir = os.path.dirname(currentdir)
    backenddir = os.path.join(parentdir, 'backend')
    sys.path.insert(0, backenddir)
    new_data = file
    response = client.post("/buffer/insert-data/", json=new_data)
    print(response)
    assert response.status_code == 200
    assert response.json() == {"message": "Buffer updated successfully"}

def test_split_data():
    response = client.post("/split-data/")
    assert response.status_code == 200
    assert response.json() == {"message": "Data processed and split successfully"}

def test_insert_data():
    response = client.post("/insert-data/")
    assert response.status_code == 200
    assert response.json() == {"message": "Data inserted into Weaviate successfully"}

def test_query_response():
    try:
        response = client.get("/query/?prompt=How%20much%20does%20it%20cost%20to%20study%20at%20harvard&n_items=5")
        assert response.status_code == 200
        json_response = response.json()
        print("Response JSON:", json_response)  # Print the actual response
        assert isinstance(json_response, list)
        for item in json_response:
            assert 'chunk_id' in item
            assert 'content' in item
            # Add other necessary assertions here
    except Exception as e:
        print(f"Test failed with exception: {e}")
        raise e

# Running the test directly
if __name__ == "__main__":
    setup_module(None)
    test_buffer_insert_data()
    test_split_data()
    test_insert_data()
    test_query_response()
