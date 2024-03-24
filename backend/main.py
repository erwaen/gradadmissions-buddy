from typing import Union, Dict
from pydantic import BaseModel

from fastapi import FastAPI

import os
from dotenv import  load_dotenv
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)

from langchain_openai import ChatOpenAI

app = FastAPI()
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

class ApiIN(BaseModel):
    consulta: str = "hola"
    number: int

class TokenUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

class ResponseMetadata(BaseModel):
    token_usage: TokenUsage
    model_name: str
    system_fingerprint: str
    finish_reason: str
    logprobs: Union[Dict, str]  # Assuming logprobs can be null/None which translates to a Python `None`

class ApiOUT(BaseModel):
    content: str
    additional_kwargs: Dict
    #response_metadata: ResponseMetadata
    type: str
    name: str
    id: str
    example: bool



@app.post("/", response_model=ApiOUT)
def read_root(body: ApiIN):
    # user = db.get_user(id=1)
    # return user 
    raise NotImplemented

@app.get("/",response_model=ApiOUT)
#de momento estoy usando strings como input, xd
def get_test(body:str):
    print(body)
    # out = model.invoke(body)
    out = {"content":"5 + 6 = 11","additional_kwargs":{},"response_metadata":{"token_usage":{"completion_tokens":7,"prompt_tokens":15,"total_tokens":22},"model_name":"gpt-3.5-turbo","system_fingerprint":"fp_3bc1b5746c","finish_reason":"stop","logprobs":"null"},"type":"ai","name":"null","id":"null","example":False}
    print(out)
    return out

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
    # return {"item_id": item_id, "q": q}
