import json
from typing import Dict
from weaviate import Any 
import weaviate.classes as wvc
from weaviate.classes.query import Filter

from weaviate.client import WeaviateClient

def query_weaviate(wclient: WeaviateClient, prompt: str, top_n: int=5):
    # Perform the initial vector search in Weaviate using contextionary
    university_collection = wclient.collections.get("UniversityData")
    result = university_collection.query.near_text(
        query=prompt,
        limit=5
    )
    # result = wclient.query.get("UniversityData", ["url", "university_name", "content", "next_id", "previous_id", "chunk_id"]) \
    #     .with_near_text({"concepts": [prompt], "certainty": 0.7}) \
    #     .with_limit(top_n) \
    #     .do()
    
    enriched_results = []
    print(result)
    for obj in result.objects:

        item =  dict(obj.properties)
        enriched_item = item.copy()

        # Fetch previous chunk's content if it exists
        if item['previous_id']:
            # previous_result = university_collection.query.fetch_object_by_id(
            #    str(item["previous_id"]) 
            # )
            previous_result = university_collection.query.fetch_objects(
                    filters=Filter.by_property("chunk_id").equal(str(item['previous_id'])),
                    limit=1
            ).objects[0]

            enriched_item['previous_content'] = None
            if previous_result:
                p_data = previous_result.properties
                enriched_item['previous_content'] = p_data['content']

        # Fetch next chunk's content if it exists
        if item['next_id']:

            # next_result = university_collection.query.fetch_object_by_id(
            #    str(item["next_id"]) 
            # )
            next_result = university_collection.query.fetch_objects(
                    filters=Filter.by_property("chunk_id").equal(str(item['next_id'])),
                    limit=1
            ).objects[0]

            enriched_item['next_content'] = None
            if  next_result:
                n_data = next_result.properties
                enriched_item['next_content'] = n_data['content']

        enriched_results.append(enriched_item)

    return enriched_results




def insert_into_weaviate(wclient: WeaviateClient, json_file):
    # Initialize the Weaviate client

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

    if not wclient.collections.exists(name="UniversityData"):
        _ = wclient.collections.create(
            name="UniversityData",
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai()
        )

    university_collection = wclient.collections.get(name="UniversityData")

    # if not wclient.schema.contains(class_obj):
    #     client.schema.create_class(class_obj)

    # Load data from JSON file
    with open(json_file, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:#Perdon por este parche feo xd
            return "No elements in splitted buffer to insert, did you forget split the data?"
    counter = 0

    for entry in data:
        counter+=1 
        print(counter, len(data))
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

        university_collection.data.insert(properties=properties, uuid=uuid)
        # client.data_object.create(properties, "UniversityData", uuid=uuid)
    return {"message": "Data inserted into Weaviate successfully"}
