from fastapi import FastAPI, Query, Path
from pydantic import BaseModel
from enum import Enum
from typing import Union, List

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: Union[str, None] = None
    tax: Union[float, None] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item2",
                "price": 35.4,
                "tax": 3.2,
            }
        }

class User(BaseModel):
    username: str
    full_name: Union[str, None] = None

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/")
def read_root():
    return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/items/")
# async def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]

@app.get("/items/")
async def read_items(q: Union[List[str], None] = Query(default=None),
    r: Union[str, None] = Query(
        default=None,
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        # deprecated=True,
    )):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    if r:
        results.update({"r": r})
    return results

@app.get("/items/{item_id}")
async def read_item(
    item: Item,
    item_id: int = Path(title="The ID of the item to get", ge=1),
    q: Union[str, None] = Query(default=None, alias="item-query"), 
    short: bool = False,
):
    i = {"item_id": item_id,"item": item}
    if q:
        i.update({"q": q})
    if not short:
        i.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return i

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, user: User):
    return {"item_name": item.name,"user_name": user.username, "item_id": item_id}


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]