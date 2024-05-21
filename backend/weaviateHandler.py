import weaviate
import json 

def query_weaviate(prompt, top_n=5):
    # Initialize Weaviate client
    weaviate_url = "http://weaviate:8080"  # Replace with your Weaviate instance URL
    client = weaviate.Client(weaviate_url)

    # Perform the initial vector search in Weaviate using contextionary
    result = client.query.get("UniversityData", ["url", "university_name", "content", "next_id", "previous_id", "chunk_id"]) \
        .with_near_text({"concepts": [prompt], "certainty": 0.7}) \
        .with_limit(top_n) \
        .do()
    
    enriched_results = []

    for item in result['data']['Get']['UniversityData']:
        enriched_item = item.copy()

        # Fetch previous chunk's content if it exists
        if item['previous_id']:
            previous_result = client.query.get("UniversityData", ["content"]) \
                .with_where({
                    "path": ["chunk_id"],
                    "operator": "Equal",
                    "valueString": item['previous_id']
                }) \
                .do()
            if previous_result['data']['Get']['UniversityData']:
                enriched_item['previous_content'] = previous_result['data']['Get']['UniversityData'][0]['content']
            else:
                enriched_item['previous_content'] = None

        # Fetch next chunk's content if it exists
        if item['next_id']:
            next_result = client.query.get("UniversityData", ["content"]) \
                .with_where({
                    "path": ["chunk_id"],
                    "operator": "Equal",
                    "valueString": item['next_id']
                }) \
                .do()
            if next_result['data']['Get']['UniversityData']:
                enriched_item['next_content'] = next_result['data']['Get']['UniversityData'][0]['content']
            else:
                enriched_item['next_content'] = None

        enriched_results.append(enriched_item)

    return enriched_results




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