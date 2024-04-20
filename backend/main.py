from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# import weaviate
# from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()


# client = weaviate.Client('http://localhost:8080/')


# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

# class QueryInput(BaseModel):
#     query: str

# class QueryOutput(BaseModel):
#     response: str

# def retrieve_from_weaviate(query: str) -> str:
#     result = client.query.get("UniversityPage", ["content"]).with_near_text({
#         'concepts': [query]
#     }).do()
#     if result and result['data']['Get']['UniversityPage']:
#         return result['data']['Get']['UniversityPage'][0]['content']
#     else:
#         return ""

# @app.post("/rag", response_model=QueryOutput)
# def rag_endpoint(input: QueryInput):
#     retrieved_content = retrieve_from_weaviate(input.query)
#     if not retrieved_content:
#         raise HTTPException(status_code=404, detail="No relevant data found in Weaviate.")


#     combined_input = f"{retrieved_content}\n\n{input.query}"
#     response = combined_input
#     #response = model.invoke(combined_input)
    
#     return QueryOutput(response=str(response))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=80,reload=False)
