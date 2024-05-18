import weaviate
import json 

def insert_into_weaviate(json_file, weaviate_url):
    # Initialize the Weaviate client
    client = weaviate.Client(weaviate_url)

    # Ensure the class schema exists in Weaviate
    class_obj = {
        "class": "UniversityData",
        "properties": [
            {
                "name": "url",
                "dataType": ["string"]
            },
            {
                "name": "university_name",
                "dataType": ["string"]
            },
            {
                "name": "content",
                "dataType": ["text"]
            },
            {
                "name": "chunk_id",
                "dataType": ["uuid"]
            },
            {
                "name": "previous_id",
                "dataType": ["uuid"]
            },
            {
                "name": "next_id",
                "dataType": ["uuid"]
            }
        ]
    }

    if not client.schema.contains(class_obj):
        client.schema.create_class(class_obj)

    # Load data from JSON file
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Insert data into Weaviate
    for entry in data:
        properties = {
            "url": entry['url'],
            "university_name": entry['university_name'],
            "content": entry['content'],
            "chunk_id": entry['chunk_id'],
            "previous_id": entry['previous_id'],
            "next_id": entry['next_id']
        }

        # Use the existing UUID
        uuid = entry['id']

        client.data_object.create(properties, "UniversityData", uuid=uuid)