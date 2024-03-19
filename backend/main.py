from typing import Union
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()


class ApiIN(BaseModel):
    consulta: str = "hola"
    number: int


class ApiOUT(BaseModel):
    name: str



@app.post("/", response_model=ApiOUT)
def read_root(body: ApiIN):
    user = db.get_user(id=1)
    return user 


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
